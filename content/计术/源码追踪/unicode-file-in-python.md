Title: python加载Unicode文件
Tags: unicode
Date: 2015-12-30 22:00

python在执行一个文件时，是如何选取/决定字符编码(encoding)的？本小记试着从源码实现的角度，追踪一下它的来龙去脉。

强调一下，这里都是基于**pyhton2.7.6**版本的分析，其他版本由于没有跟进，尚无法断定实现方式发生了变化。

## 一.

首先， python读取文件头, 通过判断BOM（Byte Order Mark）判断编码信息。

```c
static char *
decoding_fgets(char *s, int size, struct tok_state *tok)
{
	...
	 if (!check_bom(fp_getc, fp_ungetc, fp_setreadl, tok))
                return error_ret(tok); //(Step1)
    ...
}


static int
check_bom(int get_char(struct tok_state *),
          void unget_char(int, struct tok_state *),
          int set_readline(struct tok_state *, const char *),
          struct tok_state *tok)
{
	int ch1, ch2, ch3;
    ch1 = get_char(tok);
    tok->decoding_state = 1;
    if (ch1 == EOF) {
        return 1;
    } else if (ch1 == 0xEF) {
        ch2 = get_char(tok);
        if (ch2 != 0xBB) {
            unget_char(ch2, tok);
            unget_char(ch1, tok);
            return 1;
        }
        ch3 = get_char(tok);
        if (ch3 != 0xBF) {
            unget_char(ch3, tok);
            unget_char(ch2, tok);
            unget_char(ch1, tok);
            return 1;
        }
    } else {
        unget_char(ch1, tok);
        return 1;
    }
    if (tok->encoding != NULL)
        PyMem_FREE(tok->encoding);
    tok->encoding = new_string("utf-8", 5);     /* resulting is in utf-8 */
    return 1;
}
```

在这里只会判断是不是utf-8，如果是就先把编码信息挂在tok中，否则跳过（缺省）。

接着，读取文件内容，从第一个非空行中判断是否有用户指定的编码信息。

这时，如果tok已经携带了编码信息（即上面的第一步已经检查到了文件实际上使用utf-8编码），这里则会进一步检查，用户指定的编码信息是否和文件本身所反映的信息一致。如果不一致，则会报一个“encoding problem: %s with BOM”的语法错误。

如果tok尚未带有编码信息，则把找到的用户指定的编码信息指派给tok。

```c
static char *
decoding_fgets(char *s, int size, struct tok_state *tok)
{
	...
	//(Step1)
	...
	    if (line != NULL && tok->lineno < 2 && !tok->read_coding_spec) {
        if (!check_coding_spec(line, strlen(line), tok, fp_setreadl)) {
            return error_ret(tok);
        }
    } //(Step2)
	...
}

static int
check_coding_spec(const char* line, Py_ssize_t size, struct tok_state *tok,
                  int set_readline(struct tok_state *, const char *))
{
    char * cs;
    int r = 1;

    if (tok->cont_line)
        /* It's a continuation line, so it can't be a coding spec. */
        return 1;
    cs = get_coding_spec(line, size);
    if (cs != NULL) {
        tok->read_coding_spec = 1;
        if (tok->encoding == NULL) {
            assert(tok->decoding_state == 1); /* raw */
            if (strcmp(cs, "utf-8") == 0 ||
                strcmp(cs, "iso-8859-1") == 0) {
                tok->encoding = cs;
            } else {
#ifdef Py_USING_UNICODE
                r = set_readline(tok, cs);
                if (r) {
                    tok->encoding = cs;
                    tok->decoding_state = -1;
                }
                else {
                    PyErr_Format(PyExc_SyntaxError,
                                 "encoding problem: %s", cs);
                    PyMem_FREE(cs);
                }
#else
                /* Without Unicode support, we cannot
                   process the coding spec. Since there
                   won't be any Unicode literals, that
                   won't matter. */
                PyMem_FREE(cs);
#endif
            }
        } else {                /* then, compare cs with BOM */
            r = (strcmp(tok->encoding, cs) == 0);
            if (!r)
                PyErr_Format(PyExc_SyntaxError,
                             "encoding problem: %s with BOM", cs);
            PyMem_FREE(cs);
        }
    }
    return r;
}

static char *
get_normal_name(char *s)        /* for utf-8 and latin-1 */
{
    char buf[13];
    int i;
    for (i = 0; i < 12; i++) {
        int c = s[i];
        if (c == '\0')
            break;
        else if (c == '_')
            buf[i] = '-';
        else
            buf[i] = tolower(c);
    }
    buf[i] = '\0';
    if (strcmp(buf, "utf-8") == 0 ||
        strncmp(buf, "utf-8-", 6) == 0)
        return "utf-8";
    else if (strcmp(buf, "latin-1") == 0 ||
             strcmp(buf, "iso-8859-1") == 0 ||
             strcmp(buf, "iso-latin-1") == 0 ||
             strncmp(buf, "latin-1-", 8) == 0 ||
             strncmp(buf, "iso-8859-1-", 11) == 0 ||
             strncmp(buf, "iso-latin-1-", 12) == 0)
        return "iso-8859-1";
    else
        return s;
}
```

如果找不到用户指定的编码信息，而且也无法从文件BOM中找到合适的编码信息, 则把该文本当做ascii编码处理。

在这种情况下，会进一步检查文件中的每一个字符是否是ascii字符（是否>127），如果出现了非ascii字符，则会把定位到的这个字符报错:

```c
static char *
decoding_fgets(char *s, int size, struct tok_state *tok)
{
	...
	//(Step1)
	...
 	//(Step2)
	...
	#ifndef PGEN
    /* The default encoding is ASCII, so make sure we don't have any
       non-ASCII bytes in it. */
    if (line && !tok->encoding) {
        unsigned char *c;
        for (c = (unsigned char *)line; *c; c++)
            if (*c > 127) {
                badchar = *c;
                break;
            }
    }
    if (badchar) {
        char buf[500];
        /* Need to add 1 to the line number, since this line
           has not been counted, yet.  */
        sprintf(buf,
            "Non-ASCII character '\\x%.2x' "
            "in file %.200s on line %i, "
            "but no encoding declared; "
            "see http://www.python.org/peps/pep-0263.html for details",
            badchar, tok->filename, tok->lineno + 1);
        PyErr_SetString(PyExc_SyntaxError, buf);
        return error_ret(tok);
    }
#endif
    return line;   //(Step3)
	...
}
```

错误信息就是经常会遇到的这个：
 ** "Non-ASCII character '\\x%.2x' " ... **


另外, 在python判定文本为缺省ascii编码类型时，tok->encoding为空；否则, 语法树根节点node的类型(n_type)则为encoding_decl。这个过程是在parsetok(...)中完成的。

```c
static node *
parsetok(struct tok_state *tok, grammar *g, int start, perrdetail *err_ret,
         int *flags)
{
	...
	    } else if (tok->encoding != NULL) {
        /* 'nodes->n_str' uses PyObject_*, while 'tok->encoding' was
         * allocated using PyMem_
         */
        node* r = PyNode_New(encoding_decl);
        if (r)
            r->n_str = PyObject_MALLOC(strlen(tok->encoding)+1);
        if (!r || !r->n_str) {
            err_ret->error = E_NOMEM;
            if (r)
                PyObject_FREE(r);
            n = NULL;
            goto done;
        }
        strcpy(r->n_str, tok->encoding);
        PyMem_FREE(tok->encoding);
        tok->encoding = NULL;
        r->n_nchildren = 1;
        r->n_child = n;
        n = r;
    }

done:
    PyTokenizer_Free(tok);

    return n
}
```

总结一下：

1. 如果python通过BOM推导出了该文本是utf-8编码，用户可以再次用-*-coding:utf-8-*-指定，也可以不指定。但如果指定了，则要求coding后面的编码方式和BOM是一致的，否则会报语法错误"**encoding problem: %s with BOM**"。
2. 如果python无法通过BOM推导出该文本是utf-8编码，则python会利用用户给出的-*-coding:xxx-*-信息指定编码格式。
3. 如果python和用户都没有（或无法）显式给出编码格式，则python将此文本当做ascii格式对待。
4. 如果python将文本当做ascii对待，则要求内容中不能出现非ascii字符（>127）。 否则会报语法错误"**Non-ASCII character '\\x%.2x'**"。




## 二.

我们在做python CAPI编程的时候，用户可以自行利用其中的一个CPI **"PyRun_FileExFlags(..., PyCompilerFlags *flags)"** 来执行一个python文件（python自己也是利用这个CAPI来完成execfile(...)方法的）。
这里，最后一个参数**PyCompilerFlags *flags**是一个编译选项，可以通过它来”硬性“指定一种编码方式。

**PyCompilerFlags utf8Flag = { PyCF_SOURCE_IS_UTF8 }**

如果用这种方式"硬性"指定编码方式，python则会使用用户指定的编码格式。

但是，仔细看下面给出的代码就会发现，这里有一个重要前提， 那就是python自己没有推导出应该用什么格式编码。
（即node->n_type != encoding_decl, 也即python自己认为是ascii编码）。

换言之，如果python之前已经推导出了该文本为非ascii编码，那就不允许用户自己将PyCompilerFlags加上“PyCF_SOURCE_IS_UTF8”这么个标志位， 否则， python依然会抛出一个语法错误。**“encoding declaration in Unicode string”。**

```c
mod_ty
PyParser_ASTFromFile(FILE *fp, const char *filename, int start, char *ps1,
                     char *ps2, PyCompilerFlags *flags, int *errcode,
                     PyArena *arena)

{
	...
	 node *n = PyParser_ParseFileFlagsEx(fp, filename, &_PyParser_Grammar,
                            start, ps1, ps2, &err, &iflags); // (Step 1-3)
	...
	if (n) {
        flags->cf_flags |= iflags & PyCF_MASK;
        mod = PyAST_FromNode(n, flags, filename, arena); // (Step 4)
        PyNode_Free(n);
        return mod;
    }
    ...
}

mod_ty
PyAST_FromNode(const node *n, PyCompilerFlags *flags, const char *filename,
               PyArena *arena)
{
	...
	if (flags && flags->cf_flags & PyCF_SOURCE_IS_UTF8) {
        c.c_encoding = "utf-8";
        if (TYPE(n) == encoding_decl) {
            ast_error(n, "encoding declaration in Unicode string");
            goto error;
        }
    } else if (TYPE(n) == encoding_decl) {
        c.c_encoding = STR(n);
        n = CHILD(n, 0);
    } else {
        c.c_encoding = NULL;
	...
}
```

这样就出现了一个非常怪异而尴尬的境况： 只有文本本身以原始的ascii编码，用户在使用CAPI PyRun_FileExFlags（...）才能指定UTF8的编译标志。

但文本因为自身编码(ascii)的原因无法包含非ascii字符， 即便能够包含，python也不会允许在它认为是ascii编码的情况下出现非ascii字符。 这就使得UTF8编译标志位的作用形如鸡肋。

反过来，如果文本本身指定了UTF8编码（无论是通过BOM还是用户将#-*-coding:utf-8-*-写入文本），那在这里就不能指定PyCF_SOURCE_IS_UTF8这个编译标志位，而是让python自己推导。否则，就会抛出语法错误 **"encoding declaration in Unicode string"。**

可能背后基于的逻辑是，python如此说，“喂， 我已经（通过BOM或者用户指定#-*-coding:xxx-*-）发现这个文本已经声明了编码信息，你(CAPI 使用者)不能再指定它（为PyCF_SOURCE_IS_UTF8）了”.

而对此我想对它回应的设计台词是，“如果文本只能允许ascii编码，那我指定PyCF_SOURCE_IS_UTF8又有什么意义呢”？

怎么看都像是个python的bug。:(

继续总结，

+ 如果python将文本当做非ascii对待， 则用户在自行使用CAPI PyRun_FileExFlags(...)时，不允许自行指定“PyCF_SOURCE_IS_UTF8”的编译选项，否则会报语法错误 "**encoding declaration in Unicode string**"


再强调一次，这里都是基于**pyhton2.7.6**版本的分析，其他版本由于没有跟进，尚无法断定实现方式发生了变化。

#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

AUTHOR = u'Jayson.Li'
SITENAME = u'侧写流光与独行 <br/> Walks and Flows'
SITENAME_ABBR = u'侧写'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'cn'
DEFAULT_DATE = u'fs'

OUTPUT_PATH = '../web'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
WITH_FUTURE_DATES = True
# Blogroll
# LINKS = (('Pelican', 'http://getpelican.com/'),
#         ('Python.org', 'http://python.org/'),
#         ('Jinja2', 'http://jinja.pocoo.org/'),
#         ('You can modify those links in your config file', '#'),)

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 7

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = 'forked_themes/waterspill'

LOAD_CONTENT_CACHE = False

STATIC_PATHS = ['images']

DEFAULT_DATE_FORMAT = "%x - %a"


PLUGIN_PATHS = ['plugins/']
PLUGINS = ['subfolderascat']
# subfolderascat configs
SUBFOLDERASCAT_PATH = PATH
SUBFOLDERASCAT_EXC_FOLDERS = ['pages', 'images']

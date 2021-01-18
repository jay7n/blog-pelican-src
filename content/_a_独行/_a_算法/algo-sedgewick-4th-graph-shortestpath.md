Title: 读书笔记  Algorithms-4th-by-sedgewick  Shortest Paths
Date: 2020-02-05
Summary: 有关《算法》第4版-章节4.4-"最短路径"的一些速记



近期我一直在读Robert Sedgewick所著的《算法》第4版，收益良多。

本文是有关章节4.4 Shortest Paths "最短路径"的读书笔记。



## 1. Edge Relaxtion And Vertex Relaxtion

### 1.1 Edge Relaxtion

* 假设在一张图G中，点S为"求最短路径"问题的起点。另外，存在一条由两点A, B构成的边E(A->B)。起点S到A存在一条"目前已知"（即在进行中的当前时刻）的最短路径P(S--->A)，同样S到B也存在一条P(S--->B)。

* 对E(A->B)的Edge Relaxtion指的是这样一个操作：我们判断路径P(S--->A)的权重加上E(A->B)的权重是否小于路径P(S--->B)的权重？如果小于，则表示经由S--->A->B这条线路抵达点B的权重更低，那么路径P(S--->B)的信息应该更新为S--->A->B这条；如果不小于，则表示S--->B目前依然是权重最低的，那么保持不变即可。

* 由此可以推论，进行完一次Edge Relaxtion操作后，**"P(S--->B) 的权重 <= P(S--->A)+E(A->B) 的权重"**这个关系是永恒成立的。

* **可见Edge Relaxtion关心的是起点S到某条有向边的终点（这个例子中的点B）的权重最低的路径。**这个操作是以"边"为维度的、局部即时行为，不考虑全局也不考虑最终结果。同时，它也是这个算法体系中最小的原子操作了。之后所有考虑的算法，都是建立在这个基础原子操作上更宏观的行为。

* 用"Relaxtion"一词形容这种行为，是来源于"橡皮筋（rubber band）"的比喻。当你"Relaxing（放松）"一条绷紧的橡皮筋的话，它最终的结果应该就是最短的路径了。



### 1.2 Vertex Relaxtion

* 一张有向图G中，对于任意一个点A，有可能存在多条出射边E(A->B)（指向后继节点B的边）。那么对每一条这样的边E做Edge Relaxtion操作，就等同于对点A做Vertex Relaxtion操作。

* Vertex Relaxtion操作把关注点聚焦到了在Edge Relaxtion关系中的点A。**等于为点A"批处理"执行了围绕它的出射边的Edge Relaxtion操作**。因此Vertex Relaxtion可以看做是对Edge Relaxtion更靠上的一层封装。

* 注意，对点A进行一次Vertex Relaxtion操作，虽然执行的对象是点A，但并非影响起点S到A的最短路径P(S--->A)；相反，其结果是更新了点A的"每一个相邻出射节点B"的最短路径P(S--->B)。因此这个操作导致节点A的每一个出射节点B都满足 **"P(S--->B) 的权重 <= P(S--->A)+E(A->B) 的权重"** 这个关系。



## 2. Shortest Path Tree (SPT)

* 经典的算法里对最短路径的求解一般不是单点对单点的算法（当然算法稍加改造也可以满足这个诉求）。而是以某个点为起点（我们称为起点S），求解从起点S开始，抵达有向图G中其他每个点的最短路径。这样就会生成一棵以起点S为根的最短路径树（Shortest Path Tree）。

* 当最短路径树（Shortest Path Tree）生成的时候，即可知道起点S到有向图G中其他每一个节点的最短路径，以及对应的最短路径权重。

* 下面的所有算法，都是以如何生成SPT的话题进行讨论的。



## 3. Dijkstra's Algorithm

### 3.1 核心思想

* 有向图G中，将起点S的最短路径权重设置为0（因为P(S--->S)的权重为0），其它所有节点的最短路径权重初始化为Infinity(P(S--->N)的权重为无限大)。

* 准备一个优先队列PQ，将起点S放入PQ中，然后重复执行以下步骤：

    1. 取出PQ中最短路径权重**最小**的点（一开始就是S），将其移出PQ， 然后对这个点进行Vertex Relaxtion操作。

    2. 我们知道Vertex Relaxtion操作是对其"批处理"执行了围绕它的每一条出射边的Edge Relaxtion操作。如果它的相邻出射节点的权重发生了更新（即意味着经由此点到出射节点的路径更短），那么就把该出射节点放入PQ中。

    3. 当PQ中元素为空时，意味着SPT生成，算法结束；否则回到第一步。



### 3.2 我的思考之一：究竟是否可以有负权重（negative weights）？

* 书中在算法一开始的时候就提出，Dijkstra算法适用于非负权重"non-negative"的有向图。查阅了google很多的资料后，也都是这样说。比如：[这篇](https://stackoverflow.com/questions/13159337/why-doesnt-dijkstras-algorithm-work-for-negative-weight-edges)， [这篇](https://stackoverflow.com/questions/6799172/negative-weights-using-dijkstras-algorithm/6799344#6799344)，还有[这篇](https://cs.stackexchange.com/questions/19771/why-does-dijkstras-algorithm-fail-on-a-negative-weighted-graphs)。

* 其大致的原因是，图中每个节点只会做一次Vertex Relaxtion操作（这点在下面有讨论），但可能会做遇到多次Edge Relaxtion。Dijkstra算法是基于"做过Vertex Relaxtoin操作节点，之后再遇到Edge Relaxtion时，一定会大于当前的路径权重"这个事实。但如果有负权重，那就未必会"大于"了。于是所有的结论都不成立了。而对于这个理论的解释，我也是理解并认可的。

* **但现在问题来了**。书中呈现的是上述3.1算法描述的代码实现。而根据这个算法实现，我发现**即便有负值权重，也不会影响最后结果的正确性**；不止如此，我还发现，在这个实现中，**即便每次从PQ中挑选的不是"最小的点"，也不会影响最后结果的正确性**。

* 因为我发现在这个算法实现中，某个节点在进入PQ再被移出后，其他节点的Edge Relaxtion动作仍然可以使这个节点"**重入（ re-entrance）**"到PQ中，这样一来Vertex Relaxtion就不会只遍历一次了。**这个算法的实现与书中（以及大部分资料）所说的"non-negative"的解释有矛盾，这究竟是怎么回事呢？**

* 经过反复校验，排除了自身理解错误的可能性外，我又到google上搜索可能会有的解释。最后终于发现[这样一篇帖子](https://stackoverflow.com/a/55596739/1324190)，直击命中！

  * 这篇帖子说，实际上Dijkstra算法有三种变形版本。**大部分的结论说"不允许负权重的Dijkstra算法"指的是前两个版本。而 第三个版本（"允许重入(re-entrance)"）其实是允许负权重的。**

  * （当然，即便允许负权重，但无论如何也不允许负权重环（negative weights cycle）。这点在下文会有讨论。）

  * 按这个解释，书中提供的实现版本，其实就是版本三。因此这个实现支持负权重的有向图。只是说，这个算法处理负权重的图时，**虽然正确性没有问题，但性能会遭受影响（因为可能出现反复的"重入"）。**

  * 巧的是，这篇帖子贴出了和我读的同一本书（算法第4版）的线上引用。在线上的版本中，其中一个Q&A回答了这个问题：

    > **Q.** Does Dijkstra's algorithm work with negative weights?
    >
    > **A.** Yes and no. There are two shortest paths algorithms known as *Dijkstra's algorithm*, depending on whether a vertex can be enqueued on the priority queue more than once. When the weights are nonnegative, the two versions coincide (as no vertex will be enqueued more than once). The version implemented in [DijkstraSP.java](https://algs4.cs.princeton.edu/44sp/DijkstraSP.java.html) (which allows a vertex to be enqueued more than once) is correct in the presence of negative edge weights (but no negative cycles) but its running time is exponential in the worst case. (We note that [DijkstraSP.java](https://algs4.cs.princeton.edu/44sp/DijkstraSP.java.html) throws an exception if the edge-weighted digraph has an edge with a negative weight, so that a programmer is not surprised by this exponential behavior.) If we modify [DijkstraSP.java](https://algs4.cs.princeton.edu/44sp/DijkstraSP.java.html) so that a vertex cannot be enqueued more than once (e.g., using a `marked[]` array to mark those vertices that have been relaxed), then the algorithm is guaranteed to run in *E* log *V* time but it may yield incorrect results when there are edges with negative weights.

  * 但奇怪的是，我读的纸质版（*人民邮电出版社，2012年3月第一版*）却找不到这个Q&A。不知是哪里不对。

  * 最后，我偶然发现这个帖子的作者是位中国人，她在[知乎上也贡献了一个中文的版本](https://www.zhihu.com/question/21620069/answer/24518138)。表示感谢~
    

### 3.3 我的思考之二：会有多少次Vertex Relaxtion操作?

* 重温本文1.2的最后一点。一次对某节点进行Vertex Relaxtion的操作，带来的结果不是对该节点自身的最短路径权重更新，而是它所有的相邻出射节点的最短路径权重更新。

* 那么让我们问一个问题：在Dijksktra算法中，会有多少次Vertex Relaxtion操作呢？以及，是否会对某个节点有重复遍历到的Vertex Relaxtion操作呢（即之前某个节点做过一次Vertex Relaxtion，后来的步骤中又做了一次）？

    * 答案是，在有向图G中，有多少个节点就会有多少次Vertex Relaxtion操作；以及，不会有重复遍历的Vertex Relaxtion操作。

    * 原因在于，首先每一次放入PQ中的节点，其记录的权重都是该节点当前被更新为最短路径的权重。而从PQ中取出元素时，也挑选的是权重最小的节点。**这样的操作方式，会保证该节点的权重只需要遍历这么一次，就是最终的最短路径权重**。之后的操作中，如果因为其他节点做Vertex Relaxtion导致此节点受到影响时（比如该节点是其他节点的相邻出射节点），**那么经由其他节点抵达该节点的路径权重一定会大于当前节点自身的路径权重**，从而无法引起它们的Edge Relaxtion行为。**再次重申，背后的原因就是每次都是从PQ中取出了最小的元素导致。**

* 复习一下。现在让我们换个问题：在Dijkstra算法中，为什么一定要从PQ中选择一个最小的元素？能否我们随便使用一个容器（而非PQ），然后每次取元素的时候，从中随便取出一个元素？这样会有什么问题呢？

    * 本质的原因就在于上述一点。如果不以"取出最小的元素"这种操作进行的话，上面的结论就无法保证了。这样可能会有多于总节点数量的Vertex Relaxtion操作。也就是说，某些节点会被多次Vertex Relaxtion操作遍历到。**但如3.2中的结论所说，其最终结果的正确性依然是对的，然而性能会受到不小的影响。**
      

### 3.3 IndexMinPQ





## 4. Topological Sort For Edge-weighted DAG

## 5. Negative Weights And Longest Paths

## 6. Parallel Job Scheduling(PJS) Problem And Critical Path

## 7. PJS with Relative Deadlines And Negative Cycles

## 8. Shortest Paths in General Edge-weighted Digraphs

## 9. Queue-based Bellman-Ford

## 10. Applicaton Case: Arbitrage

## 11. Summary




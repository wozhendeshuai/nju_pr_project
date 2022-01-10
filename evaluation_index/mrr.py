import numpy as np


def mrr(rel_true, rel_pred):
    """
    MRR Mean Reciprocal Rank, 平均倒数排名是一个国际上通用的对搜索算法进行评价的机制，
    其评估假设是基于唯一的一个相关结果，即第一个结果匹配，分数为 1 ，第二个匹配分数为 0.5，第 n 个匹配分数为 1/n，
    如果没有匹配的句子分数为0。最终的分数为所有得分之和。
    这个是最简单的一个，因为它的评估假设是基于唯一的一个相关结果，
    如q1的最相关是排在第3位，q2的最相关是在第4位，那么MRR=(1/3+1/4)/2，
    MRR方法主要用于寻址类检索（Navigational Search）或问答类检索（Question Answering）。
    Args:
        rel_true (1-D Array): relevance lists for particular user, (n_songs,)
        rel_pred (1-D Array): predicted relevance lists, (n_pred,)
    Returns:
        mrr (float):找到该Query第一次出现最大的位置的倒数
    """
    if rel_pred.__len__() < 1:
        return 0
    temp_max = -1
    for key in rel_true:
        if key > temp_max:
            temp_max = key
    # 累加评分
    max_index = 1
    for i in range(rel_pred.__len__()):
        if temp_max == rel_pred[i]:
            max_index = i + 1

    return 1 / max_index

# print(mrr([4, 3, 3, 2, 1, 1, 0, 0, 0], [2, 3, 1, 3, 4, 0, 0, 0, 1]))

import numpy as np


def ndcg(rel_true, rel_pred, p=None, form="linear"):
    """ Returns normalized Discounted Cumulative Gain
    Args:
        rel_true (1-D Array): relevance lists for particular user, (n_songs,)
        rel_pred (1-D Array): predicted relevance lists, (n_pred,)
        p (int): particular rank position
        form (string): two types of nDCG formula, 'linear' or 'exponential'
    Returns:
        ndcg (float): normalized discounted cumulative gain score [0, 1]
    """
    rel_true = np.sort(rel_true)[::-1]
    rel_pred = np.array(rel_pred)

    p = min(len(rel_true), min(len(rel_pred), p))

    # 因为索引是从0开始的，正常应该加1，但是从0开始，log(0+1)则等于无穷大，所以这里面加的是2，如果索引是从1开始，则加的是1，所以感觉跟上面的公式不一致，其实是一样的。
    discount = 1 / (np.log2(np.arange(p) + 2))

    if form == "linear":
        idcg = np.sum((rel_true[:p] + 1) * discount)
        dcg = np.sum((rel_pred[:p] + 1) * discount)
        # print(rel_true)
    elif form == "exponential" or form == "exp":
        idcg = np.sum([2 ** x  for x in rel_true[:p]] * discount)
        dcg = np.sum([2 ** x  for x in rel_pred[:p]] * discount)
    else:
        raise ValueError("Only supported for two formula, 'linear' or 'exp'")

    return dcg / idcg

#print(ndcg([2, 1, 0, 0], [0, 1, 2, 0],4,"exp"))

# print(ndcg([1, 2, 3], [2, 3, 1], 3))
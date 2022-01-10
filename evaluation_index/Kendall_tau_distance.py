import numpy as np


def kendall_tau_distance(rel_true, rel_pred):
    '''
    也就是两个排序间，评价存在分歧的对的数量。具体定义如下：
    如果两个排序完全一样。则Kendall tau distance位0。否则，如果两个排序完全相反，则为n(n−1)/2n(n−1)/2。
    通常 Kendall tau distance都会通过除以n(n−1)/2n(n−1)/2来归一化。
    https://www.pianshen.com/article/3105911974/
    '''
    if rel_pred.__len__() <= 1:
        return 0
    len = rel_true.__len__()
    different_num = 0
    for true_i in range(len):
        # 记录两个列表最左边的值
        true_left = rel_true[true_i]
        pred_left = rel_pred[true_i]
        for true_j in range(true_i+1, len):
            # 记录两个列表最右边的值
            true_right = rel_true[true_j]
            pred_right = rel_pred[true_j]
            # 记录在两个列表中相同位置的值是否存在大小不一致
            if true_left == true_right and pred_left != pred_right:
                different_num = different_num + 1
            elif true_left < true_right and pred_left > pred_right:
                different_num = different_num + 1
            elif true_left > true_right and pred_left < pred_right:
                different_num = different_num + 1
    to_1 = len * (len - 1) / 2
    return different_num / to_1


print(kendall_tau_distance([4], [3]))

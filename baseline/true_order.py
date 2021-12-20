# 根据已有数据得到真实的排序
def get_true_order_dict(response_time, first_response_time_dict):
    # 传入一个无序的response list，以及与response_time_dict对应,找出该response列表中的五等分点，以及这五等分点对应的值分别是多少
    true_rate_label_dict = {}
    response_time.sort()
    # 求五等分点
    l = response_time.__len__()
    idx = [int(l / 5), int(l * 2 / 5), int(l * 3 / 5), int(l * 4 / 5)]
    threshold = []
    for i in idx:
        threshold.append(response_time[i])
    # 根据响应速度打标签 1,2,3,4,5
    for key in first_response_time_dict.keys():
        tmp = 0
        key_response_time = first_response_time_dict[key]
        if key_response_time < threshold[0]:
            tmp = 4
        elif key_response_time < threshold[1]:
            tmp = 3
        elif key_response_time < threshold[2]:
            tmp = 2
        elif key_response_time < threshold[3]:
            tmp = 1
        else:
            tmp = 0
        true_rate_label_dict[key] = tmp
    return true_rate_label_dict

import json
from datetime import datetime


def get_developer_stats(labels_dict):
    """
       计算pr作者在代码仓的总提交成功率
       labels_dict
       {
            52950: '{"0": {"id": 300136587, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/cla:%20yes", "name": "cla: yes", "color": "009800", "default": false, "node_id": "MDU6TGFiZWwzMDAxMzY1ODc=", "description": null}, "1": {"id": 1169365682, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/size:L", "name": "size:L", "color": "adafea", "default": false, "node_id": "MDU6TGFiZWwxMTY5MzY1Njgy", "description": "CL Change Size: Large"}}'
       }
       转为json后计算json的长度
       """
    re_dict = {}
    return re_dict


def get_pr_author_accept_rate(pr_dict):
    """
       计算pr作者在代码仓的总提交成功率
       labels_dict
       {
            52948: {'created_time': datetime.datetime(2021, 11, 4, 22, 23, 45), 'closed_time': None, 'merged_time': None, 'pr_user_name': 'EwoutH'},
        }
       转为json后计算json的长度
       如果该pr_author还未提交过，我们认为该pr_user_name的接受概率为1，拒绝概率为0
       """
    re_dict = {}
    # 用于保存维护比当前遍历的pr先创建的pr
    temp_dict = {}

    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        closed_time = ((pr_dict[key]['closed_time'] != None) and pr_dict[key]['closed_time'] or datetime.now())
        merged_time = pr_dict[key]['merged_time']
        pr_user_name = pr_dict[key]['pr_user_name']
        # 当tempdict无数据时，要新增一条
        if temp_dict.__len__() == 0:
            temp_dict[key] = pr_dict[key]
            re_dict[key] = {}
            re_dict[key]['self_accept_rate'] = 1
            re_dict[key]['self_contribution_rate'] = 0
            re_dict[key]['self_closed_num_rate'] = 0
            re_dict[key]['project_accept_rate'] = 1
        else:
            # 统计pr的数量
            pr_num = 0
            # 统计pr的接受数量
            pr_accept_num = 0
            # 统计pr的关闭数量
            pr_close_num = 0
            # 统计该pr提交者pr的数量
            self_pr_num = 0
            # 该pr提交者提交的pr在该pr之前接受的数量
            self_pr_accept_num = 0
            # 该pr提交者提交的pr在该pr之前关闭的数量
            self_pr_close_num = 0
            for temp_key in temp_dict.keys():
                temp_created_time = temp_dict[temp_key]['created_time']
                temp_closed_time = ((temp_dict[temp_key]['closed_time'] != None) and temp_dict[temp_key][
                    'closed_time'] or datetime.now())
                temp_merged_time = temp_dict[temp_key]['merged_time']
                temp_user_name = temp_dict[temp_key]['pr_user_name']
                # 对于所有pr的累计
                pr_num = pr_num + 1
                if temp_merged_time is not None and temp_merged_time < created_time:
                    pr_accept_num = pr_accept_num + 1
                if temp_closed_time is not None and temp_closed_time < created_time:
                    pr_close_num = pr_close_num + 1
                if temp_user_name.__eq__(pr_user_name):
                    if temp_created_time < created_time:
                        self_pr_num = self_pr_num + 1
                    if temp_closed_time is not None and temp_closed_time < created_time:
                        self_pr_close_num = self_pr_close_num + 1
                    if temp_merged_time is not None and temp_merged_time < created_time:
                        self_pr_accept_num = self_pr_accept_num + 1
            re_dict[key] = {}
            if self_pr_num == 0:
                re_dict[key]['self_accept_rate'] = 1
                re_dict[key]['self_closed_num_rate'] = 0
            else:
                re_dict[key]['self_accept_rate'] = self_pr_accept_num / self_pr_num
                re_dict[key]['self_closed_num_rate'] = self_pr_close_num / self_pr_num
            re_dict[key]['self_contribution_rate'] = self_pr_num / pr_num
            re_dict[key]['project_accept_rate'] = pr_accept_num / pr_num
            temp_dict[key] = pr_dict[key]
    return re_dict

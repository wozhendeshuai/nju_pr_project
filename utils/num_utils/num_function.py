import json
from datetime import datetime


def get_label_count(labels_dict):
    """
       计算每个pr中的label的数量
       labels_dict
       {
            52950: '{"0": {"id": 300136587, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/cla:%20yes", "name": "cla: yes", "color": "009800", "default": false, "node_id": "MDU6TGFiZWwzMDAxMzY1ODc=", "description": null}, "1": {"id": 1169365682, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/size:L", "name": "size:L", "color": "adafea", "default": false, "node_id": "MDU6TGFiZWwxMTY5MzY1Njgy", "description": "CL Change Size: Large"}}'
       }
       转为json后计算json的长度
       """
    re_dict = {}
    for key in labels_dict.keys():
        labels_json = json.loads(labels_dict[key])
        re_dict[key] = len(labels_json)
    return re_dict


def get_workload(pr_dict):
    """
       计算每个pr提交时，整个项目中打开的pr数，也就是在之前的pr_pre 的创建时间早于该pr的创建时间，且，pr_pre的关闭时间晚于该pr的创建时间
        {
            52949:
            {
                'created_time': datetime.datetime(2021, 11, 4, 23, 37, 50),
                'closed_time': None},
            }
       当closed_time为空时，以当前的时间代替，说明还未关闭
       """
    re_dict = {}
    # 用于保存维护比当前遍历的pr先创建还未关闭的pr
    temp_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        closed_time = ((pr_dict[key]['closed_time'] != None) and pr_dict[key]['closed_time'] or datetime.now())
        # 当tempdict无数据时，要新增一条
        if temp_dict.__len__() == 0:
            temp_dict[key] = pr_dict[key]
            re_dict[key] = 0
        else:
            # 计数
            count = 0
            remove_list = []  # 存储需要被移除的key值
            for temp_key in temp_dict.keys():
                temp_created_time = pr_dict[temp_key]['created_time']
                temp_closed_time = ((pr_dict[temp_key]['closed_time'] != None) and pr_dict[temp_key][
                    'closed_time'] or datetime.now())
                if temp_created_time < created_time and temp_closed_time > created_time:
                    count = count + 1
                else:
                    remove_list.append(temp_key)
            for temp_key in remove_list:
                temp_dict.pop(temp_key)
            re_dict[key] = count
            temp_dict[key] = pr_dict[key]
    return re_dict


def get_prev_prs(user_pr_dict):
    """
       获取该pr提交之前，提交者提交的pr数量
       user_pr_dict
       {
           52943: {'pr_user_name': 'vict-guo'},
        }
    """
    re_dict = {}
    temp_dict = {}
    for key in user_pr_dict.keys():
        pr_user_name = user_pr_dict[key]['pr_user_name']
        count = 0
        if temp_dict.__len__() > 0:
            for temp_key in temp_dict.keys():
                temp_user_name = temp_dict[temp_key]['pr_user_name']
                if temp_user_name == pr_user_name:
                    count = count + 1
        temp_dict[key] = user_pr_dict[key]
        re_dict[key] = count
    return re_dict


def get_change_num(pr_change_dict):
    """
       获取该pr提交之前，提交者提交的pr中的代码更改总数
       user_pr_dict
       {
           16380: {'pr_user_name': 'av8ramit', 'changed_line_num': 4227}
        }
    """
    re_dict = {}
    temp_dict = {}
    for key in pr_change_dict.keys():
        pr_user_name = pr_change_dict[key]['pr_user_name']
        count = 0
        if temp_dict.__len__() > 0:
            for temp_key in temp_dict.keys():
                temp_user_name = temp_dict[temp_key]['pr_user_name']
                if temp_user_name == pr_user_name:
                    count = count + temp_dict[temp_key]['changed_line_num']
        temp_dict[key] = pr_change_dict[key]
        re_dict[key] = count
    return re_dict


def get_accept_num(pr_dict):
    """
       获取该pr提交之前，提交者提交的pr的接受总数
       user_pr_dict
       {
           52946: {'pr_user_name': 'mihaimaruseac', 'merged_at': datetime.datetime(2021, 11, 4, 20, 56, 56)},
        }
    """
    re_dict = {}
    temp_dict = {}
    for key in pr_dict.keys():
        pr_user_name = pr_dict[key]['pr_user_name']
        count = 0
        if temp_dict.__len__() > 0:
            for temp_key in temp_dict.keys():
                temp_user_name = temp_dict[temp_key]['pr_user_name']
                temp_merged_at = temp_dict[temp_key]['merged_at']
                if temp_user_name == pr_user_name and temp_merged_at is not None:
                    count = count + 1
        temp_dict[key] = pr_dict[key]
        re_dict[key] = count
    return re_dict


def get_close_num(pr_dict):
    """
       获取该pr提交之前，提交者提交的pr的关闭总数
       user_pr_dict
       {
           52949: {'pr_user_name': 'tlemo', 'created_time': datetime.datetime(2021, 11, 4, 23, 37, 50), 'closed_time': None, 'merged_at': None},
        }
    """
    re_dict = {}
    temp_dict = {}
    for key in pr_dict.keys():
        pr_user_name = pr_dict[key]['pr_user_name']
        count = 0
        if temp_dict.__len__() > 0:
            created_time = pr_dict[key]['created_time']
            closed_time = ((pr_dict[key]['closed_time'] is not None) and pr_dict[key]['closed_time'] or datetime.now())
            for temp_key in temp_dict.keys():
                temp_user_name = temp_dict[temp_key]['pr_user_name']
                temp_created_time = temp_dict[temp_key]['created_time']
                temp_closed_time = ((temp_dict[temp_key]['closed_time'] is not None) and temp_dict[temp_key][
                    'closed_time'] or datetime.now())
                if temp_user_name == pr_user_name and temp_created_time < created_time < temp_closed_time and temp_closed_time >= closed_time:
                    count = count + 1
        temp_dict[key] = pr_dict[key]
        re_dict[key] = count
    return re_dict


def get_review_num(pr_dict):
    """
     该pr作者之前评审过多少pr review_comments
       user_pr_dict
       {
           52949: {'pr_user_name': 'tlemo', 'created_time': datetime.datetime(2021, 11, 4, 23, 37, 50), 'closed_time': None, 'merged_at': None},
        }
    """
    re_dict = {}
    return re_dict



def get_content_people( number, content,re_set):
    # 找出content里面参与人数
    if number == 0:
        return re_set
    index = 0
    content_json = json.loads(content)
    while index < len(content_json):
        # 有的是没有user这个属性的
        if content_json[index]["user"] is None:
            user_name = None
        else:
            user_name = content_json[index]["user"]["login"]
            re_set.add(user_name.__str__())
        index = index + 1
    return re_set

def get_participants_count(pr_dict):
    """
     该pr的参与者之和，包括提交者，评论者，评审者人数
       user_pr_dict
       {
          52949: {
          'pr_user_name': 'tlemo',
          'created_time': datetime.datetime(2021, 11, 4, 23, 37, 50),
          'closed_time': None,
          'comments_number': 0,
          'comments_content': '[]',
          'review_comments_number': 0,
          'review_comments_content': '[]'
          },
        }
    """
    re_dict = {}
    for key in pr_dict.keys():
        pr_user_name = pr_dict[key]['pr_user_name']
        comments_number = pr_dict[key]['comments_number']
        comments_content = pr_dict[key]['comments_content']
        review_comments_number = pr_dict[key]['review_comments_number']
        review_comments_content = pr_dict[key]['review_comments_content']
        name_set=set()
        name_set.add(pr_user_name.__str__())
        try:
            name_set=get_content_people(comments_number,comments_content,name_set)
            name_set=get_content_people(review_comments_number,review_comments_content,name_set)
        except Exception as e:
            print(str(key) + "      ")
            print(e)
            break
        re_dict[key] = name_set.__len__()
    return re_dict

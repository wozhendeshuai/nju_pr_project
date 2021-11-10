from datetime import datetime
import dateutil
import json
from utils.time_utils import time_reverse


def project_age(project_dict):
    """
    计算项目的创建时间距今的月份差
    project_dict的组成
    {
        45717250:
        {
            'created_time': datetime.datetime(2015, 11, 7, 1, 19, 20),
            'updated_time': datetime.datetime(2021, 11, 5, 9, 14, 49),
            'pushed_time': datetime.datetime(2021, 11, 5, 9, 14, 21)
        }
    }
    计算方法，利用当前时间-created_time计算月份
    返回的dict为{id：相差的月份}
    """
    re_dict = {}
    for key in project_dict.keys():
        created_time = project_dict[key]['created_time']
        time_now = datetime.now()
        year1 = time_now.year
        year2 = created_time.year
        month1 = time_now.month
        month2 = created_time.month
        num = (year1 - year2) * 12 + (month1 - month2)
        re_dict[key] = num
    return re_dict


def get_first_content_time(pr_user_name, number, content):
    # 找出content里面最早评论的时间
    if number == 0:
        return None
    index = 0
    re_time = None
    content_json = json.loads(content)
    while index < len(content_json):
        # 有的是没有user这个属性的
        if content_json[index]["user"] == None:
            user_name = None
        else:
            user_name = content_json[index]["user"]["login"]
        comments_time = time_reverse(content_json[index]["created_at"])
        if pr_user_name == user_name:
            index = index + 1
            continue
        elif re_time == None:
            re_time = comments_time
        elif comments_time < re_time:
            re_time = comments_time
        index = index + 1
    return re_time


def get_waiting_time(pr_dict):
    """
    获取pr中comments/review_comments中第一个非pr提交者评论时间
    pr_dict:
    {
        52949:
        {
            'created_time': datetime.datetime(2021, 11, 4, 23, 37, 50),
            'comments_number': 0,
            'comments_content': '[]',
            'review_comments_number': 0,
            'review_comments_content': '[]',
            'pr_user_name': 'tlemo'
        },
    }
    返回的dict为{id：相差的月份}
    调用get_first_content_time获取当前content json中最早非本人评论时间，再找出review/comments最早的时间减去创建时间，即为等待时间
    """
    re_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        # 有的还没有close也没有comments所以这时候需要用现在的时间，代替关闭时间
        closed_time = ((pr_dict[key]['closed_time'] != None) and pr_dict[key]['closed_time'] or datetime.now())
        pr_user_name = pr_dict[key]['pr_user_name']
        comments_number = pr_dict[key]['comments_number']
        comments_content = pr_dict[key]['comments_content']
        review_comments_number = pr_dict[key]['review_comments_number']
        review_comments_content = pr_dict[key]['review_comments_content']
        try:
            first_comments_time = get_first_content_time(pr_user_name, comments_number, comments_content)
            first_review_time = get_first_content_time(pr_user_name, review_comments_number, review_comments_content)
        except Exception as e:
            print(str(key) + "      ")
            print(e)
            break
        final_time = None
        # 对无评论的进行处理
        if first_comments_time is None:
            if first_review_time is None:
                final_time = closed_time
            else:
                final_time = first_review_time
        elif first_review_time is None:
            final_time = first_comments_time
        else:
            if first_review_time < first_comments_time:
                final_time = first_review_time
            else:
                final_time = first_comments_time
        re_dict[key] = (final_time - created_time).total_seconds() / 60
    return re_dict


def is_weekday_commit(pr_dict):
    """
    获取pr的创建时间
    pr_dict:
    {
        52949:datetime.datetime(2021, 11, 4, 23, 37, 50),
    }
    返回的dict为{id：是否是工作日} 1 代表是周一至周五，0代表非周一周五
    """
    re_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]
        if created_time.isoweekday() <= 5:
            re_dict[key] = 1
        else:
            re_dict[key] = 0
    return re_dict

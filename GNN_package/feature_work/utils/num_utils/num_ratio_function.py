from datetime import datetime
import dateutil
import json
from utils.time_utils import time_reverse


def get_pr_author_rate(pr_dict):
    """
       计算pr作者在代码仓的总提交成功率,接受概率，总的贡献给率，代码仓的贡献率
       labels_dict
       {
            52948: {
            'created_time': datetime.datetime(2021, 11, 4, 22, 23, 45),
            'closed_time': None,
            'merged_time': None,
            'pr_user_name': 'EwoutH'
            },
        }
       转为json后计算json的长度
       如果该pr_author还未提交过，我们认为该pr_user_name的接受概率为1，拒绝概率为0
       返回值
       {
             52949: {
             'self_accept_rate': 1.0,
             'self_closed_num_rate': 1.0,
             'self_contribution_rate': 5.17437648763324e-05,
             'project_accept_rate': 0.7065093656214426
             },
       }
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


def get_project_line_rate(pr_dict):
    """
       计算project上一周的平均删除，增加，改变的行的数量
       labels_dict
       {
            52950: {'created_time': datetime.datetime(2021, 11, 5, 0, 4, 17), 'total_add_line': 254, 'total_delete_line': 205}
        }
       转为json后计算json的长度
       如果该pr_author还未提交过，我们认为该pr_user_name的接受概率为1，拒绝概率为0
       返回值
       {
             52949: {
             'deletions_per_week': 63469.40064102564,
             'additions_per_week': 194976.12820512822,
             'changes_per_week': 258445.52884615384
             },
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}

    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        total_add_line = pr_dict[key]['total_add_line']
        total_delete_line = pr_dict[key]['total_delete_line']
        total_change_line = total_add_line + total_delete_line
        created_week = created_time.isocalendar()
        year = created_week[0]
        week = created_week[1]
        # 累计多少周
        contain_week = 0
        # 累计增加了多少行
        temp_add_line = 0
        # 累计删除了多少行
        temp_delete_line = 0
        # 累计改变了多少行
        temp_change_line = 0

        for temp_year in temp_dict.keys():
            for temp_week in temp_dict[temp_year].keys():
                if temp_year == year and temp_week == week:
                    break
                else:
                    contain_week = contain_week + 1
                    temp_add_line = temp_add_line + temp_dict[temp_year][temp_week]["total_add_line"]
                    temp_delete_line = temp_delete_line + temp_dict[temp_year][temp_week]["total_delete_line"]
                    temp_change_line = temp_change_line + temp_dict[temp_year][temp_week]["total_change_line"]
        re_dict[key] = {}
        if contain_week == 0:
            re_dict[key]['deletions_per_week'] = 0
            re_dict[key]['additions_per_week'] = 0
            re_dict[key]['changes_per_week'] = 0
        else:
            re_dict[key]['deletions_per_week'] = temp_delete_line / contain_week
            re_dict[key]['additions_per_week'] = temp_add_line / contain_week
            re_dict[key]['changes_per_week'] = temp_change_line / contain_week
        # 计算完后，放入新的数据到temp_dict中
        if temp_dict.__contains__(year) is False:
            # 年份为key，周数为第二个key
            temp_dict[year] = {}
            temp_dict[year][week] = {}
            temp_dict[year][week]["total_add_line"] = total_add_line
            temp_dict[year][week]["total_delete_line"] = total_delete_line
            temp_dict[year][week]["total_change_line"] = total_change_line
        else:
            if temp_dict[year].__contains__(week) is False:
                temp_dict[year][week] = {}
                temp_dict[year][week]["total_add_line"] = total_add_line
                temp_dict[year][week]["total_delete_line"] = total_delete_line
                temp_dict[year][week]["total_change_line"] = total_change_line
            else:
                temp_dict[year][week]["total_add_line"] = total_add_line + temp_dict[year][week]["total_add_line"]
                temp_dict[year][week]["total_delete_line"] = total_delete_line + temp_dict[year][week][
                    "total_delete_line"]
                temp_dict[year][week]["total_change_line"] = total_change_line + temp_dict[year][week][
                    "total_change_line"]

    return re_dict


def get_line_weekday_rate(pr_dict):
    """
       计算pr根据所在周的周几，判断该周几的平均修改的行数，增加的数量，删除的数量
       labels_dict
       {
            52950: {'created_time': datetime.datetime(2021, 11, 5, 0, 4, 17), 'total_add_line': 254, 'total_delete_line': 205}
        }
       转为json后计算json的长度
       如果该pr_author还未提交过，我们认为该pr_user_name的接受概率为1，拒绝概率为0

       返回值
       {
            52949: {
                'per_lines_deleted_week_days': 799.7732574679943,
                'per_lines_added_week_days': 3677.2375533428167,
                'per_lines_changed_week_days': 4477.010810810811
            },
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        total_add_line = pr_dict[key]['total_add_line']
        total_delete_line = pr_dict[key]['total_delete_line']
        total_change_line = total_add_line + total_delete_line
        created_week = created_time.isocalendar()
        week_day = created_week[2]
        # 该日有多少pr
        re_dict[key] = {}
        if temp_dict.__contains__(week_day) is False:
            re_dict[key]['per_lines_changed_week_days'] = 0
            re_dict[key]['per_lines_added_week_days'] = 0
            re_dict[key]['per_lines_deleted_week_days'] = 0
            temp_dict[week_day] = {}
            temp_dict[week_day]["total_add_line"] = total_add_line
            temp_dict[week_day]["total_delete_line"] = total_delete_line
            temp_dict[week_day]["total_change_line"] = total_change_line
            temp_dict[week_day]["contain_pr"] = 1
        else:
            re_dict[key]['per_lines_deleted_week_days'] = temp_dict[week_day]["total_delete_line"] / \
                                                          temp_dict[week_day]["contain_pr"]
            re_dict[key]['per_lines_added_week_days'] = temp_dict[week_day]["total_add_line"] / temp_dict[week_day][
                "contain_pr"]
            re_dict[key]['per_lines_changed_week_days'] = temp_dict[week_day]["total_change_line"] / \
                                                          temp_dict[week_day]["contain_pr"]
            temp_dict[week_day]["total_add_line"] = total_add_line + temp_dict[week_day]["total_add_line"]
            temp_dict[week_day]["total_delete_line"] = total_delete_line + temp_dict[week_day]["total_delete_line"]
            temp_dict[week_day]["total_change_line"] = total_change_line + temp_dict[week_day]["total_change_line"]
            temp_dict[week_day]["contain_pr"] = 1 + temp_dict[week_day]["contain_pr"]
    return re_dict


def get_project_line_churn_rate(pr_dict):
    """
       计算pr的平均删除，增加，改变的行的数量,不是一周一个单位了，而是pr的数量
       labels_dict
       {
            52949: {'total_add_line': 13, 'total_delete_line': 6},
        }
       转为json后计算json的长度
       返回值
       {
         52949: {
         'deletions_per_pr': 1024.7502845907068,
         'additions_per_pr': 3147.855634895995,
         'changes_per_pr': 4172.605919486702
         },
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}
    for key in pr_dict.keys():
        total_add_line = pr_dict[key]['total_add_line']
        total_delete_line = pr_dict[key]['total_delete_line']
        total_change_line = total_add_line + total_delete_line
        re_dict[key] = {}
        if temp_dict.__len__() == 0:
            temp_dict["total_add_line"] = total_add_line
            temp_dict["total_delete_line"] = total_delete_line
            temp_dict["total_change_line"] = total_change_line
            temp_dict["total_pr_num"] = 1
            re_dict[key]['deletions_per_pr'] = 0
            re_dict[key]['additions_per_pr'] = 0
            re_dict[key]['changes_per_pr'] = 0
        else:
            re_dict[key]['deletions_per_pr'] = temp_dict["total_delete_line"] / temp_dict["total_pr_num"]
            re_dict[key]['additions_per_pr'] = temp_dict["total_add_line"] / temp_dict["total_pr_num"]
            re_dict[key]['changes_per_pr'] = temp_dict["total_change_line"] / temp_dict["total_pr_num"]
            temp_dict["total_add_line"] = total_add_line + temp_dict["total_add_line"]
            temp_dict["total_delete_line"] = total_delete_line + temp_dict["total_delete_line"]
            temp_dict["total_change_line"] = total_change_line + temp_dict["total_change_line"]
            temp_dict["total_pr_num"] = 1 + temp_dict["total_pr_num"]
    return re_dict


def get_commits_average(pr_dict):
    """
       根据当前pr创建的时间，计算所有pr的平均提交数量
       labels_dict
       {
            52950: {'created_time': datetime.datetime(2021, 11, 5, 0, 4, 17), 'closed_time': datetime.datetime(2021, 11, 5, 15, 40, 43), 'commit_number': 1}
        }

       返回值
       {
            52946: 21.698354377975573,
            pr_number:commits_average
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        closed_time = pr_dict[key]['closed_time']
        commit_number = pr_dict[key]['commit_number']
        if temp_dict.__len__() == 0:
            temp_dict["total_commit_number"] = commit_number
            temp_dict["pr_num"] = 1
            re_dict[key] = 0
        else:
            re_dict[key] = temp_dict["total_commit_number"] / temp_dict["pr_num"]
            temp_dict["total_commit_number"] = temp_dict["total_commit_number"] + commit_number
            temp_dict["pr_num"] = temp_dict["pr_num"] + 1
    return re_dict


def get_avg_comments(pr_dict):
    """
       根据当前pr创建的时间，计算所有pr的平均评论数，以及合并的pr的平均评论数
       labels_dict
       {
            52950: {
            'created_time': datetime.datetime(2021, 11, 5, 0, 4, 17),
            'closed_time': datetime.datetime(2021, 11, 5, 15, 40, 43),
            'merged_time': None, 'comments_number': 1}
        }
       转为json后计算json的长度
       如果该pr_author还未提交过，我们认为该pr_user_name的接受概率为1，拒绝概率为0

       返回值
       {
            52948: {
            'comments_per_closed_pr': 5.77386725063872,
            'comments_per_merged_pr': 5.345905961622968
            },
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        re_dict[key] = {}
        if temp_dict.__len__() == 0:
            re_dict[key]['comments_per_closed_pr'] = 0
            re_dict[key]['comments_per_merged_pr'] = 0
            temp_dict[key] = pr_dict[key]
        else:
            # 关闭的pr评论累计数
            closed_comments_number = 0
            # 合并的pr评论累计数
            merged_comments_number = 0
            # 关闭的pr数
            closed_pr_number = 0
            # 合并的pr数
            merged_pr_number = 0
            # 此处遍历符合条件的pr和评论数，并累加起来，用于后面除
            for temp_key in temp_dict.keys():
                temp_closed_time = temp_dict[temp_key]["closed_time"]
                temp_merged_time = temp_dict[temp_key]["merged_time"]
                temp_comments_number = temp_dict[temp_key]["comments_number"]
                if temp_closed_time is not None and temp_closed_time <= created_time:
                    closed_pr_number = closed_pr_number + 1
                    closed_comments_number = closed_comments_number + temp_comments_number
                if temp_merged_time is not None and temp_merged_time <= created_time:
                    merged_pr_number = merged_pr_number + 1
                    merged_comments_number = merged_comments_number + temp_comments_number
            if closed_pr_number == 0:
                re_dict[key]['comments_per_closed_pr'] = 0
            else:
                re_dict[key]['comments_per_closed_pr'] = closed_comments_number / closed_pr_number
            if merged_pr_number == 0:
                re_dict[key]['comments_per_merged_pr'] = 0
            else:
                re_dict[key]['comments_per_merged_pr'] = merged_comments_number / merged_pr_number
            temp_dict[key] = pr_dict[key]
    return re_dict


def get_avg_latency(pr_dict):
    """
       计算pr的合并时间，计算，从pr的打开状态到合并状态的平均天数，以及从打开状态到关闭状态的平均天数
       labels_dict
       {
             52950: {
             'created_time': datetime.datetime(2021, 11, 5, 0, 4, 17),
             'closed_time': datetime.datetime(2021, 11, 5, 15, 40, 43),
             'merged_time': None
             },
        }
       返回值
       {
         52948: {
         'close_latency': 19.34282287919078,
         'merge_latency': 12.824740002929545
         },
       }
       """
    re_dict = {}
    # 用于存储之前周改变的行数
    temp_dict = {}
    for key in pr_dict.keys():
        created_time = pr_dict[key]['created_time']
        closed_time = pr_dict[key]["closed_time"]
        merged_time = pr_dict[key]["merged_time"]
        close_day = 0
        merge_day = 0
        # 当天合并或者关闭，算1
        if closed_time is not None:
            close_day = (closed_time - created_time).days + 1
        if merged_time is not None:
            merge_day = (merged_time - created_time).days + 1
        re_dict[key] = {}
        if temp_dict.__len__() == 0:
            re_dict[key]['merge_latency'] = 0
            re_dict[key]['close_latency'] = 0
        else:
            # 关闭的pr天数累计数
            closed_days_number = 0
            # 合并的pr天数累计数
            merged_days_number = 0
            # 关闭的pr数
            closed_pr_number = 0
            # 合并的pr数
            merged_pr_number = 0
            # 此处遍历符合条件的pr和评论数，并累加起来，用于后面除
            for temp_key in temp_dict.keys():
                temp_closed_time = temp_dict[temp_key]["closed_time"]
                temp_merged_time = temp_dict[temp_key]["merged_time"]
                temp_close_day = temp_dict[temp_key]["close_day"]
                temp_merge_day = temp_dict[temp_key]["merge_day"]
                if temp_closed_time is not None and temp_closed_time <= created_time:
                    closed_pr_number = closed_pr_number + 1
                    closed_days_number = closed_days_number + temp_close_day
                # 这样也把没有合并的pr给过滤掉了
                if temp_merged_time is not None and temp_merged_time <= created_time:
                    merged_pr_number = merged_pr_number + 1
                    merged_days_number = merged_days_number + temp_merge_day
            if closed_pr_number == 0:
                re_dict[key]['close_latency'] = 0
            else:
                re_dict[key]['close_latency'] = closed_days_number / closed_pr_number

            if merged_pr_number == 0:
                re_dict[key]['merge_latency'] = 0
            else:
                re_dict[key]['merge_latency'] = merged_days_number / merged_pr_number
        temp_dict[key] = pr_dict[key]
        temp_dict[key]["close_day"] = close_day
        temp_dict[key]["merge_day"] = merge_day
    return re_dict

from networkx.algorithms.shortest_paths import weighted
from networkx.classes import ordered
from numpy.lib.function_base import append
from pymysql import NULL
import getData
import csv
import torch
import pandas as pd
import numpy as np
import dgl
import dgl.nn as dglnn
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from dgl.data.utils import generate_mask_tensor
from dgl.data import DGLDataset
import torch
from sklearn.metrics import hamming_loss
import json
from utils.date_utils.date_function import is_weekday_commit \
    , project_age, get_latency_after_response, get_waiting_time
from utils.time_utils import time_reverse
from utils.num_utils.num_function import get_label_count \
    , get_workload, get_prev_prs, get_change_num \
    , get_accept_num, get_close_num, get_review_num \
    , get_participants_count
from utils.str_utils.str_function import wordCount
from utils.num_utils.num_ratio_function import get_pr_author_rate \
    , get_project_line_rate, get_line_weekday_rate, get_project_line_churn_rate \
    , get_commits_average, get_avg_comments, get_avg_latency
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# 从数据库获取数据
raw_data = getData.getDataFromSql(
    "select * from pr_self"
)
print(len(raw_data))  ##查看PR数量

# 标记有用的PR自身信息的下标
useful_features_index = [0,  ##pr_number
                         2,  ##repo_name
                         3,  ##pr_user_id
                         5,  ##pr_author_association
                         8,  ##labels
                         10,  ##created_at
                         12,  ##closed_at
                         13,  ##merged_at
                         14,  ##merged
                         16,  ##mergeable_state
                         18,  ##assignees_content
                         20,  ##comments_number
                         21,  ##comments_content
                         22,  ##review_comments_number
                         23,  ##review_comments_content
                         24,  ##commit_number
                         26,  ##changed_file_num
                         27,  ##total_add_line
                         28,  ##total_delete_line
                         4,  ##pr_user_name
                         11,  ##updated_at
                         6,  ##title
                         7,  ##body
                         ]

##保留有用的属性特征
selected_data = []
for item in raw_data:
    tmp = []
    for i in useful_features_index:
        tmp.append(item[i])
    selected_data.append(tmp)

process_data = []
count = 0
# 从有用的特征中获取所有的数据，并将可以直接转换为数字的数据进行初步转换
for item in selected_data:
    tmp = []
    ##pr_number
    tmp.append(item[0])
    ##repo_name
    tmp.append(item[1])
    ##pr_user_id
    tmp.append(item[2])
    ####pr_author_association
    if item[3] == 'CONTRIBUTOR':
        tmp.append(0)
    elif item[3] == 'MEMBER':
        tmp.append(1)
    elif item[3] == 'NONE':
        tmp.append(2)
    else:
        tmp.append(3)

    ##labels
    if item[4] == '{}':
        tmp.append(0)
    else:
        tmp.append(1)

    ##created_at
    tmp.append(item[5])
    ##closed_at
    tmp.append(item[6])
    ##merged_at
    tmp.append(item[7])

    ##merged
    tmp.append(item[8])

    ##mergeable_state
    if item[9] == 'unknown':
        tmp.append(0)
    elif item[9] == 'blocked':
        tmp.append(1)
    elif item[9] == 'dirty':
        tmp.append(2)
    else:
        tmp.append(3)

    ##assignees_content
    if item[10] == '{}':
        tmp.append(0)
    else:
        tmp.append(1)

    ##comments_number
    tmp.append(item[11])

    ##comments_content
    tmp.append(item[12])
    ##review_comments_number
    tmp.append(item[13])
    ##review_comments_content
    tmp.append(item[14])
    ##commit_number
    tmp.append(item[15])
    ##changed_file_num
    tmp.append(item[16])
    ##total_add_line
    tmp.append(item[17])
    ##total_delete_line
    tmp.append(item[18])

    ##pr_username
    tmp.append(item[19])

    ##pr_id
    tmp.append(count)

    ##updated_at
    tmp.append(item[20])

    ##content
    tmp.append(item[4])

    ##title
    tmp.append(item[21])

    ##body
    tmp.append(item[22])

    count += 1
    process_data.append(tmp)

print(count)

##获得仓库年龄
repo_data = getData.getDataFromSql(
    "select repo_id,repo_name\
        ,project_created_at,project_updated_at\
        ,project_pushed_at from pr_repo"
)

proj_age = []
for item in repo_data:
    tmp = []
    tmp.append(('created_time', item[2]))
    tmp.append(('updated_time', item[3]))
    tmp.append(('pushed_time', item[4]))
    tmp = dict(tmp)
    proj_age.append((item[0], tmp))

proj_age = dict(proj_age)
proj_age = project_age(proj_age)

Proj_age = []
for item in process_data:
    for i in repo_data:
        if item[1] == i[1]:
            Proj_age.append(proj_age[i[0]])

##是否为工作日
is_weekday = []
for item in process_data:
    is_weekday.append((item[20], item[5]))
is_weekday = dict(is_weekday)
is_weekday = is_weekday_commit(is_weekday)

###获取PR的label数
label_dict = []
for item in process_data:
    label_dict.append((item[20], item[22]))
label_dict = dict(label_dict)
label_dict = get_label_count(label_dict)

##获取每个PR提交时，open PR的数量
workload = []
for item in process_data:
    tmp = []
    tmp.append(('created_time', item[5]))
    tmp.append(('closed_time', item[6]))
    tmp = dict(tmp)
    workload.append((item[20], tmp))

workload = dict(workload)
workload = get_workload(workload)

# 获取该pr提交之前，提交者提交的pr数量

pre_prs = []
for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp = dict(tmp)
    pre_prs.append((item[20], tmp))

pre_prs = dict(pre_prs)
pre_prs = get_prev_prs(pre_prs)

# 获取该pr提交之前，提交者提交的pr中的代码更改总数
change_num = []
for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('changed_line_num', item[17] + item[18]))
    tmp = dict(tmp)
    change_num.append((item[20], tmp))

change_num = dict(change_num)
change_num = get_change_num(change_num)

# 获取该pr提交之前，提交者提交的pr的接受总数
accept_num = []
for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('merged_at', item[7]))
    tmp = dict(tmp)
    accept_num.append((item[20], tmp))

accept_num = dict(accept_num)
accept_num = get_accept_num(accept_num)

# 获取该pr提交之前，提交者提交的pr的关闭总数
close_num = []

for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('created_time', item[5]))
    tmp.append(('closed_time', item[6]))
    tmp.append(('merged_at', item[7]))
    tmp = dict(tmp)
    close_num.append((item[20], tmp))

close_num = dict(close_num)
close_num = get_close_num(close_num)

# 该pr作者之前评审过多少pr review_comments
review_num = []

for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('created_time', item[5]))
    tmp.append(('closed_time', item[6]))
    tmp.append(('review_comments_number', item[13]))
    tmp.append(('review_comments_content', item[14]))
    tmp = dict(tmp)
    review_num.append((item[20], tmp))

review_num = dict(review_num)
review_num = get_review_num(review_num)

# 获取该pr的参与者之和，包括提交者，评论者，评审者人数
participants_count = []
for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('created_time', item[5]))
    tmp.append(('closed_time', item[6]))
    tmp.append(('comments_number', item[11]))
    tmp.append(('comments_content', item[12]))
    tmp.append(('review_comments_number', item[13]))
    tmp.append(('review_comments_content', item[14]))
    tmp = dict(tmp)
    participants_count.append((item[20], tmp))

participants_count = dict(participants_count)
participants_count = get_participants_count(participants_count)

title_words = []
for item in process_data:
    title_words.append(wordCount(item[23]))

body_words = []
for item in process_data:
    body_words.append(wordCount(item[24]))

key_words = ['bug', 'document', 'feature', 'improve', 'refactor']
has_key_words = []
for item in process_data:
    tmp = []
    if item[24] is None:
        tmp = [0, 0, 0, 0, 0]
    else:
        for k in key_words:
            if k in item[24]:
                tmp.append(1)
            else:
                tmp.append(0)
    has_key_words.append(tmp)

#  获取pr作者在代码仓的总提交成功率,接受概率，总的贡献给率，代码仓的贡献率

pr_data = []
for item in process_data:
    tmp = []
    tmp.append(('pr_user_name', item[19]))
    tmp.append(('created_time', item[5]))
    tmp.append(('closed_time', item[6]))
    tmp.append(('comments_number', item[11]))
    tmp.append(('comments_content', item[12]))
    tmp.append(('review_comments_number', item[13]))
    tmp.append(('review_comments_content', item[14]))
    tmp.append(('total_add_line', item[17]))
    tmp.append(('total_delete_line', item[18]))
    tmp.append(('commit_number', item[15]))
    tmp.append(('merged_time', item[7]))
    tmp = dict(tmp)
    pr_data.append((item[20], tmp))

pr_data = dict(pr_data)

#  获取pr作者在代码仓的总提交成功率,接受概率，总的贡献给率，代码仓的贡献率
pr_author_rate = get_pr_author_rate(pr_data)
#    {
#          52949: {
#          'self_accept_rate': 1.0,
#          'self_closed_num_rate': 1.0,
#          'self_contribution_rate': 5.17437648763324e-05,
#          'project_accept_rate': 0.7065093656214426
#          },
#    }


# 获取project上一周的平均删除，增加，改变的行的数量
project_line_rate = get_project_line_rate(pr_data)
#    {
#          52949: {
#          'deletions_per_week': 63469.40064102564,
#          'additions_per_week': 194976.12820512822,
#          'changes_per_week': 258445.52884615384
#          },
#    }


# 计算pr根据所在周的周几，判断该周几的平均修改的行数，增加的数量，删除的数量
line_weekday_rate = get_line_weekday_rate(pr_data)
#    {
#         52949: {
#             'per_lines_deleted_week_days': 799.7732574679943,
#             'per_lines_added_week_days': 3677.2375533428167,
#             'per_lines_changed_week_days': 4477.010810810811
#         },
#    }


# 获取pr的平均删除，增加，改变的行的数量,不是一周一个单位了，而是pr的数量
project_line_churn_rate = get_project_line_churn_rate(pr_data)
# print(project_line_churn_rate)
#    {
#      52949: {
#      'deletions_per_pr': 1024.7502845907068,
#      'additions_per_pr': 3147.855634895995,
#      'changes_per_pr': 4172.605919486702
#      },
#    }


# 根据当前pr创建的时间，计算所有pr的平均提交数量
commits_average = get_commits_average(pr_data)
# print(commits_average)
#     {
#         52946: 21.698354377975573,
#         pr_number:commits_average
#    }


# 根据当前pr创建的时间，计算所有pr的平均评论数，以及合并的pr的平均评论数
avg_comments = get_avg_comments(pr_data)
# print(avg_comments)

#    {
#         52948: {
#         'comments_per_closed_pr': 5.77386725063872,
#         'comments_per_merged_pr': 5.345905961622968
#         },
#    }

# 计算pr的合并时间，计算，从pr的打开状态到合并状态的平均天数，以及从打开状态到关闭状态的平均天数
avg_latency = get_avg_latency(pr_data)
#     {
#      52948: {
#      'close_latency': 19.34282287919078,
#      'merge_latency': 12.824740002929545
#      },
#    }

X_dispersed = []  ##离散类型值
X_successive = []  ##连续类型值

##item[3] PR提交者项目身份,item[4]PR是否含有label,
# item[9] PR的mergable_state
# ,item[10] 是否有assignees_content,item[11],comment数量
# item[13] review_comment数量,item[15] commit数量
# ,item[16] 修改文件数,item[17] 增加代码行数,item[18] 删除代码行数

for item in process_data:
    X_dispersed.append([item[3], item[4], item[9]
                           , item[10]])

for item in process_data:
    X_successive.append([item[11], item[13], item[15]
                            , item[16], item[17], item[18]])

for i in range(len(X_dispersed)):
    X_dispersed[i].append(pr_author_rate[i]['self_accept_rate'])
    X_dispersed[i].append(pr_author_rate[i]['self_closed_num_rate'])
    X_dispersed[i].append(pr_author_rate[i]['self_contribution_rate'])
    X_dispersed[i].append(pr_author_rate[i]['project_accept_rate'])
    X_dispersed[i].append(is_weekday[i])

for i in range(len(X_successive)):
    # X_successive[i].append(Proj_age[i])    
    X_successive[i].append(label_dict[i])
    X_successive[i].append(workload[i])
    X_successive[i].append(pre_prs[i])
    X_successive[i].append(change_num[i])
    X_successive[i].append(accept_num[i])
    X_successive[i].append(close_num[i])
    X_successive[i].append(review_num[i])
    X_successive[i].append(participants_count[i])
    X_successive[i].append(title_words[i])
    X_successive[i].append(body_words[i])
    for k in has_key_words[i]:
        X_successive[i].append(k)

    X_successive[i].append(project_line_rate[i]['deletions_per_week'])
    X_successive[i].append(project_line_rate[i]['additions_per_week'])
    X_successive[i].append(project_line_rate[i]['changes_per_week'])
    X_successive[i].append(line_weekday_rate[i]['per_lines_deleted_week_days'])
    X_successive[i].append(line_weekday_rate[i]['per_lines_added_week_days'])
    X_successive[i].append(line_weekday_rate[i]['per_lines_changed_week_days'])
    X_successive[i].append(project_line_churn_rate[i]['deletions_per_pr'])
    X_successive[i].append(project_line_churn_rate[i]['additions_per_pr'])
    X_successive[i].append(project_line_churn_rate[i]['changes_per_pr'])
    X_successive[i].append(commits_average[i])
    X_successive[i].append(avg_comments[i]['comments_per_closed_pr'])
    X_successive[i].append(avg_comments[i]['comments_per_merged_pr'])
    X_successive[i].append(avg_latency[i]['close_latency'])
    X_successive[i].append(avg_latency[i]['merge_latency'])

###归一化
X_successive = np.array(X_successive)
mins = X_successive.min(0)  # 返回data矩阵中每一列中最小的元素，返回一个列表
maxs = X_successive.max(0)  # 返回data矩阵中每一列中最大的元素，返回一个列表
ranges = maxs - mins  # 最大值列表 - 最小值列表 = 差值列表
normData = np.zeros(np.shape(X_successive))  # 生成一个与 data矩阵同规格的normData全0矩阵，用于装归一化后的数据
row = X_successive.shape[0]  # 返回 data矩阵的行数
normData = X_successive - np.tile(mins, (row, 1))  # data矩阵每一列数据都减去每一列的最小值
normData = normData / np.tile(ranges, (row, 1))
X_successive = normData.tolist()

X = []
for i in range(len(X_dispersed)):
    tmp = []
    for j in X_dispersed[i]:
        tmp.append(j)
    for j in X_successive[i]:
        tmp.append(j)
    X.append(tmp)

##获取每个PR的响应时间
first_response_time = []
for item in process_data:
    tmp = []
    tmp.append(('created_time', item[5]))
    tmp.append(('updated_time', item[21]))
    tmp.append(('closed_time', item[6]))
    tmp.append(('comments_number', item[11]))
    tmp.append(('comments_content', item[12]))
    tmp.append(('review_comments_number', item[13]))
    tmp.append(('review_comments_content', item[14]))
    tmp.append(('pr_user_name', item[19]))
    tmp = dict(tmp)
    first_response_time.append((item[20], tmp))

first_response_time = dict(first_response_time)
first_response_time = get_waiting_time(first_response_time)

##响应时间
Y1 = []
for item in first_response_time.keys():
    Y1.append(first_response_time[item])

####响应时间
Y_1 = []
for item in Y1:
    Y_1.append(item)
##是否被合并  (70%)
Y_2 = []
for item in process_data:
    Y_2.append(item[8])

##最终的输出label [快/慢响应，是/否合并]
Y = []
for i in range(0, len(Y_1)):
    Y.append([Y_1[i], Y_2[i]])



headers = ['Id',
           'author_identity',
           'has_labels',
           'mergable_state',
           'has_assignees_content',
           'comment_num',
           'review_comment_num',
           'commit_num',
           'file_changed_num',
           'total_add_line',
           'total_delete_line',
           'self_accept_rate',
           'self_closed_num_rate',
           'self_contribution_rate',
           'project_accept_rate',
           'is_weekday',
           'label_count',
           'workload',
           'pre_prs',
           'change_num',
           'accept_num',
           'close_num',
           'review_num',
           'participants_count',
           'title_words',
           'body_words',
           'has_bug',
           'has_document',
           'has_feature',
           'has_improve',
           'has_refactor',
           'deletions_per_week',
           'additions_per_week',
           'changes_per_week',
           'per_lines_deleted_week_days',
           'per_lines_added_week_days',
           'per_lines_changed_week_days',
           'deletions_per_pr',
           'additions_per_pr',
           'changes_per_pr',
           'commits_average',
           'comments_per_closed_pr',
           'comments_per_merged_pr',
           'close_latency',
           'merge_latency',
           'response_speed',
           'if_merged']
row_data = []
count = 0

for i in range(len(X)):
    tmp = []
    tmp.append(count)
    count += 1
    for x in X[i]:
        tmp.append(x)
    for x in Y[i]:
        tmp.append(x)
    row_data.append(tmp)

# 保存数据到csv文件
with open('./nodes_data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(headers)
    for item in row_data:
        writer.writerow(item)

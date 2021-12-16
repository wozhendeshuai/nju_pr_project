from networkx.algorithms.shortest_paths import weighted
from networkx.classes import ordered
from numpy.lib.function_base import append
from pymysql import NULL
import getData
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
from utils.date_utils.date_function import is_weekday_commit\
    ,project_age,get_latency_after_response,get_waiting_time
from utils.time_utils import time_reverse
from utils.num_utils.num_function import get_label_count\
    ,get_workload,get_prev_prs,get_change_num\
    ,get_accept_num,get_close_num,get_review_num\
    ,get_participants_count
from utils.str_utils.str_function import wordCount
from utils.num_utils.num_ratio_function import get_pr_author_rate\
    ,get_project_line_rate,get_line_weekday_rate,get_project_line_churn_rate\
        ,get_commits_average,get_avg_comments,get_avg_latency
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from dgl.nn.pytorch import edge_softmax, GATConv
import csv
import torch

#从数据库获取数据
raw_data=getData.getDataFromSql(
    "select * from pr_self"
)
print(len(raw_data))##查看PR数量

useful_features_index=[0,##pr_number
    2,##repo_name
    3,##pr_user_id
    5,##pr_author_association
    8,##labels
    10,##created_at
    12,##closed_at
    13,##merged_at
    14,##merged
    16,##mergeable_state
    18,##assignees_content
    20,##comments_number
    21,##comments_content
    22,##review_comments_number
    23,##review_comments_content
    24,##commit_number
    26,##changed_file_num
    27,##total_add_line
    28,##total_delete_line
    4,##pr_user_name
    11,##updated_at
    6,##title
    7,##body
    ]



selected_data=[] ##保留有用的属性特征
for item in raw_data:
    tmp=[]
    for i in useful_features_index:
        tmp.append(item[i])
    selected_data.append(tmp)



process_data=[]
count=0
for item in selected_data:
    tmp=[]
    ##pr_number
    tmp.append(item[0])
    ##repo_name
    tmp.append(item[1])
    ##pr_user_id
    tmp.append(item[2])
    ####pr_author_association
    if item[3]=='CONTRIBUTOR':
        tmp.append(0)
    elif item[3]=='MEMBER':
        tmp.append(1)
    elif item[3]=='NONE':
        tmp.append(2)
    else:
        tmp.append(3)

    ##labels
    if item[4]=='{}':
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
    if item[9]=='unknown':
        tmp.append(0)
    elif item[9]=='blocked':
        tmp.append(1)
    elif item[9]=='dirty':
        tmp.append(2)
    else:
        tmp.append(3)

    ##assignees_content
    if item[10]=='{}':
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

    count+=1
    process_data.append(tmp)


###构造3种边
edge_source=[]
edge_target=[]

##1.相同提交者的PR之间有边：
for i in process_data:
    for j in process_data:
        if i[2]==j[2]:
            edge_source.append(i[20])
            edge_target.append(j[20])
            
# 保存数据到csv文件

headers=['SrcId','DesId','Weight']
row_data=[]

for i in range(len(edge_source)):
    tmp=[]
    tmp.append(edge_source[i])
    tmp.append(edge_target[i])
    tmp.append(1)
    row_data.append(tmp)
        
# 保存数据到csv文件
with open('./edges_data.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(headers)
    for item in row_data:
        writer.writerow(item)








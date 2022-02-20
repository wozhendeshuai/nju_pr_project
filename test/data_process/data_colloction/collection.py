import csv

import pymysql as db
import requests

from utils.num_utils.num_function import get_label_count, get_workload, get_prev_prs, get_change_num, get_accept_num, \
    get_close_num, get_participants_count, get_review_num
from utils.path_exist import path_exists_or_create
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json

# 链接数据库
database = db.connect(host='172.19.241.129', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
select_sql="select repo_name from pr_repo"
cursor.execute(select_sql)
repo_data=cursor.fetchall()
repo_list=[]
for i in range(repo_data.__len__()):
    repo_list.append(repo_data[i][0])
headers = ['repo_name',
               'per_day_open',
               'per_day_close',
               'per_day_merged',
               'per_day_created'
               ]
file_path = "./result/"
path_exists_or_create(file_path)
with open(file_path + "repo_per_collections.csv",
          'a+', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(headers)
    f.close()
for repo_name in repo_list:
    pr_sql = "select  pr_number, created_at, updated_at, closed_at, merged_at from pr_self where repo_name='" + repo_name + "'"
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    index = 0
    pr_created_dict = {}
    pr_closed_dict = {}
    pr_merged_dict = {}
    pr_dict = {}
    # 记录最早的创建时间
    early_create_date = None
    # 记录最晚的关闭时间
    later_close_date = None
    while index < data.__len__():
        pr_number = data[index][0]
        created_at = data[index][1].date()
        closed_at = (data[index][3] is not None) and data[index][3].date() or None
        merged_at = (data[index][4] is not None) and data[index][4].date() or None
        pr_dict[pr_number] = {}
        pr_dict[pr_number]["created_at"] = created_at
        pr_dict[pr_number]["closed_at"] = closed_at
        pr_dict[pr_number]["merged_at"] = merged_at
        if early_create_date is None or early_create_date > created_at:
            early_create_date = created_at
        if later_close_date is None or (closed_at is not None and later_close_date < closed_at):
            later_close_date = closed_at
        if pr_created_dict.__contains__(created_at):
            pr_created_dict[created_at] = pr_created_dict[created_at] + 1
        else:
            pr_created_dict[created_at] = 1
        if closed_at is not None:
            if pr_closed_dict.__contains__(closed_at):
                pr_closed_dict[closed_at] = pr_closed_dict[closed_at] + 1
            else:
                pr_closed_dict[closed_at] = 1
        if merged_at is not None:
            if pr_merged_dict.__contains__(merged_at):
                pr_merged_dict[merged_at] = pr_merged_dict[merged_at] + 1
            else:
                pr_merged_dict[merged_at] = 1
        index = index + 1
    pr_open_dict = {}
    for index_pr_number in pr_dict.keys():
        created_at = pr_dict[index_pr_number]["created_at"]
        closed_at = pr_dict[index_pr_number]["closed_at"]
        merged_at = pr_dict[index_pr_number]["merged_at"]
        if pr_open_dict.__contains__(created_at):
            pr_open_dict[created_at] = pr_open_dict[created_at] + 1
        else:
            temp_count_open = 1
            for temp in pr_dict.keys():
                if temp == index_pr_number:
                    continue
                temp_created_time = pr_dict[temp]["created_at"]
                temp_closed_time = pr_dict[temp]["closed_at"]
                temp_merged_time = pr_dict[temp]["merged_at"]
                if temp_created_time < created_at and (temp_closed_time is None or temp_closed_time > created_at):
                    temp_count_open = temp_count_open + 1
            pr_open_dict[created_at] = temp_count_open
    pr_created_count = 0
    pr_closed_count = 0
    pr_merged_count = 0
    pr_open_count = 0
    for temp in pr_created_dict.keys():
        pr_created_count = pr_created_count + pr_created_dict[temp]
    for temp in pr_closed_dict.keys():
        pr_closed_count = pr_closed_count + pr_closed_dict[temp]
    for temp in pr_merged_dict.keys():
        pr_merged_count = pr_merged_count + pr_merged_dict[temp]
    for temp in pr_merged_dict.keys():
        pr_merged_count = pr_merged_count + pr_merged_dict[temp]
    for temp in pr_open_dict.keys():
        pr_open_count = pr_open_count + pr_open_dict[temp]
    if early_create_date is None or later_close_date is None or pr_created_dict.__len__() == 0 or pr_closed_dict.__len__() == 0 or pr_merged_dict.__len__() == 0 or pr_open_dict.__len__() == 0:
        print(repo_name + " 平均每天创建的pr数量：" +
              str(pr_created_dict.__len__()) +
              " 平均每天关闭的pr数量：" + str(pr_closed_dict.__len__()) +
              " 平均每天合并的PR数量：" + str(pr_merged_dict.__len__()) +
              "平均每天处于打开状态PR的数量" + str(pr_open_dict.__len__()+"early_create_date"
                                      +str(early_create_date)+"later_close_date"+str(later_close_date)))
        continue
    day_len = (later_close_date-early_create_date).days
    print(repo_name + " 平均每天创建的pr数量：" +
          str(pr_created_count / pr_created_dict.__len__()) +
          " 平均每天关闭的pr数量：" + str(pr_closed_count / pr_closed_dict.__len__()) +
          " 平均每天合并的PR数量：" + str(pr_merged_count / pr_merged_dict.__len__()) +
          "平均每天处于打开状态PR的数量" + str(pr_open_count / pr_open_dict.__len__()))
    print(repo_name + " day_len平均每天创建的pr数量：" +
          str(pr_created_count / day_len) +
          " day_len平均每天关闭的pr数量：" + str(pr_closed_count / day_len) +
          " day_len平均每天合并的PR数量：" + str(pr_merged_count / day_len) +
          " day_len平均每天处于打开状态PR的数量" + str(pr_open_count / day_len))

    item_date=[repo_name,
               pr_open_count / day_len,
               pr_closed_count / day_len,
               pr_merged_count / day_len,
               pr_created_count / day_len]

    with open(file_path + "repo_per_collections.csv",'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(item_date)
        f.close()
# 关闭数据库连接
database.close()

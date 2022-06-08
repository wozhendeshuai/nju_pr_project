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
#database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='project_data_collection_db', charset='utf8')
database = db.connect(host='172.19.241.129', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
select_sql = "select repo_name from pr_repo"
cursor.execute(select_sql)
repo_data = cursor.fetchall()
repo_list = []
for i in range(repo_data.__len__()):
    repo_list.append(repo_data[i][0])
headers = ['day',
           'day_create',
           'day_close',
           'day_workload'
           ]
file_path = "./result/"
path_exists_or_create(file_path)
for repo_name in repo_list:
    with open(file_path + repo_name + "_repo_per_collections.csv",
              'w+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        f.close()
    pr_sql = "select  pr_number, created_at, updated_at, closed_at, merged_at from pr_self where repo_name='" + repo_name + "'"
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    index = 0
    pr_created_dict = {}
    pr_closed_dict = {}
    pr_dict = {}
    while index < data.__len__():
        pr_number = data[index][0]
        created_at = data[index][1].date()
        closed_at = (data[index][3] is not None) and data[index][3].date() or None
        merged_at = (data[index][4] is not None) and data[index][4].date() or None
        pr_dict[pr_number] = {}
        pr_dict[pr_number]["created_at"] = created_at
        pr_dict[pr_number]["closed_at"] = closed_at
        pr_dict[pr_number]["merged_at"] = merged_at
        if pr_created_dict.__contains__(created_at):
            pr_created_dict[created_at][pr_number] = pr_dict[pr_number]
        else:
            pr_created_dict[created_at] = {}
            pr_created_dict[created_at][pr_number] = pr_dict[pr_number]
        if closed_at is not None:
            if pr_closed_dict.__contains__(closed_at):
                pr_closed_dict[closed_at][pr_number] = pr_dict[pr_number]
            else:
                pr_closed_dict[closed_at] = {}
                pr_closed_dict[closed_at][pr_number] = pr_dict[pr_number]
        index = index + 1
    # 保存每天处于打开的PR
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

    for temp in pr_created_dict.keys():
        pr_closed_num=0
        if pr_closed_dict.__contains__(temp):
            pr_closed_num=pr_closed_dict[temp].__len__()
        item_date = [temp,
                     pr_created_dict[temp].__len__(),
                     pr_closed_num,
                     pr_open_dict[temp]]
        with open(file_path + repo_name + "_repo_per_collections.csv", 'a+', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(item_date)
            f.close()

# 关闭数据库连接
database.close()

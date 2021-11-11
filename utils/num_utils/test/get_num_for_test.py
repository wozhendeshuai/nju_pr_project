import pymysql as db
import requests

from utils.num_utils.num_function import get_label_count, get_workload, get_prev_prs, get_change_num, get_accept_num, \
    get_close_num
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json


def test_get_labels():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    labels_dict = {}
    index = 0
    while index < data.__len__():
        labels_dict[data[index][0]] = data[index][6]
        index = index + 1
    print(labels_dict)
    print(get_label_count(labels_dict))


def test_get_workload():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    pr_dict = {}
    index = 0
    while index < data.__len__():
        pr_dict[data[index][0]] = {}
        pr_dict[data[index][0]]["created_time"] = data[index][1]
        pr_dict[data[index][0]]["closed_time"] = data[index][3]
        index = index + 1
    print(pr_dict)
    print(get_workload(pr_dict))


def test_get_prev_prs():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    user_pr_dict = {}
    index = 0
    while index < data.__len__():
        user_pr_dict[data[index][0]] = {}
        user_pr_dict[data[index][0]]["pr_user_name"] = data[index][5]
        index = index + 1
    print(user_pr_dict)
    print(get_prev_prs(user_pr_dict))


def test_get_change_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    user_pr_dict = {}
    index = 0
    while index < data.__len__():
        user_pr_dict[data[index][0]] = {}
        user_pr_dict[data[index][0]]["pr_user_name"] = data[index][5]
        user_pr_dict[data[index][0]]["changed_line_num"] = data[index][9] + data[index][10]
        index = index + 1
    print(user_pr_dict)
    print(get_change_num(user_pr_dict))

def test_get_accept_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    user_pr_dict = {}
    index = 0
    while index < data.__len__():
        user_pr_dict[data[index][0]] = {}
        user_pr_dict[data[index][0]]["pr_user_name"] = data[index][5]
        user_pr_dict[data[index][0]]["created_time"] = data[index][1]
        user_pr_dict[data[index][0]]["closed_time"] = data[index][3]
        user_pr_dict[data[index][0]]["merged_at"] = data[index][4]
        index = index + 1
    print(user_pr_dict)
    print(get_accept_num(user_pr_dict))

def test_get_close_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    user_pr_dict = {}
    index = 0
    while index < data.__len__():
        user_pr_dict[data[index][0]] = {}
        user_pr_dict[data[index][0]]["pr_user_name"] = data[index][5]
        user_pr_dict[data[index][0]]["created_time"] = data[index][1]
        user_pr_dict[data[index][0]]["closed_time"] = data[index][3]
        user_pr_dict[data[index][0]]["merged_at"] = data[index][4]
        index = index + 1
    print(user_pr_dict)
    print(get_close_num(user_pr_dict))

# 数据操作部分
# SQL语句书写
pr_sql = """
select 
pr_number,
created_at,
updated_at,
closed_at,
merged_at,
pr_user_name,
labels,
state,
changed_file_num,
total_add_line,
total_delete_line
 from pr_self"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_get_close_num()
# 关闭数据库连接
database.close()

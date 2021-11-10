import pymysql as db
import requests

from utils.date_utils.date_function import project_age, get_waiting_time, is_weekday_commit, get_latency_after_response
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json


def test_month_diff():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    time_dict = {}
    index = 0
    while index < data.__len__():
        time_dict[data[index][0]] = {}
        # time_dict[data[index][0]]["created_time"]=data[index][6]
        # time_dict[data[index][0]]["updated_time"]=data[index][7]
        # time_dict[data[index][0]]["pushed_time"]=data[index][8]
        time_dict[data[index][0]]["created_time"] = data[index][1]
        time_dict[data[index][0]]["updated_time"] = data[index][2]
        time_dict[data[index][0]]["pushed_time"] = data[index][3]
        index = index + 1
    print(time_dict)
    print(project_age(time_dict))


def test_wait_time_diff():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    time_dict = {}
    index = 0
    while index < data.__len__():
        time_dict[data[index][0]] = {}
        time_dict[data[index][0]]["created_time"] = data[index][1]
        time_dict[data[index][0]]["updated_time"] = data[index][2]
        time_dict[data[index][0]]["closed_time"] = data[index][3]
        time_dict[data[index][0]]["comments_number"] = data[index][5]
        time_dict[data[index][0]]["comments_content"] = data[index][6]
        time_dict[data[index][0]]["review_comments_number"] = data[index][7]
        time_dict[data[index][0]]["review_comments_content"] = data[index][8]
        time_dict[data[index][0]]["pr_user_name"] = data[index][9]
        index = index + 1
    # print(time_dict)
    print(get_waiting_time(time_dict))

def test_get_latency_after_response():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    time_dict = {}
    index = 0
    while index < data.__len__():
        time_dict[data[index][0]] = {}
        time_dict[data[index][0]]["created_time"] = data[index][1]
        time_dict[data[index][0]]["updated_time"] = data[index][2]
        time_dict[data[index][0]]["closed_time"] = data[index][3]
        time_dict[data[index][0]]["comments_number"] = data[index][5]
        time_dict[data[index][0]]["comments_content"] = data[index][6]
        time_dict[data[index][0]]["review_comments_number"] = data[index][7]
        time_dict[data[index][0]]["review_comments_content"] = data[index][8]
        time_dict[data[index][0]]["pr_user_name"] = data[index][9]
        index = index + 1
    # print(time_dict)
    print(get_latency_after_response(time_dict))

def test_is_weekday():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    time_dict = {}
    index = 0
    while index < data.__len__():
        time_dict[data[index][0]] = data[index][1]
        index = index + 1
    # print(time_dict)
    print(is_weekday_commit(time_dict))


# 数据操作部分
# SQL语句书写
repo_sql = """select * from pr_repo"""
pr_sql = """select pr_number,created_at,updated_at,closed_at,merged_at,comments_number,comments_content,review_comments_number,review_comments_content,pr_user_name from pr_self"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_get_latency_after_response()
# 关闭数据库连接
database.close()

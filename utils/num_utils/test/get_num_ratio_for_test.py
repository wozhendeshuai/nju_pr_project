import pymysql as db
import requests

from utils.num_utils.num_ratio_function import get_developer_stats, get_pr_author_accept_rate
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json


def test_get_developer_stats():
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
    print(get_developer_stats(labels_dict))


def test_get_pr_author_accept_rate():
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
        pr_dict[data[index][0]]["merged_time"] = data[index][4]
        pr_dict[data[index][0]]["pr_user_name"] = data[index][5]
        index = index + 1
    print(pr_dict)
    print(get_pr_author_accept_rate(pr_dict))


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
total_delete_line,
comments_number,
comments_content,
review_comments_number,
review_comments_content
 from pr_self"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_get_pr_author_accept_rate()
# 关闭数据库连接
database.close()

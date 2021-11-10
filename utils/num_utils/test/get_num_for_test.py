import pymysql as db
import requests

from utils.num_utils.num_function import get_label_count
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



# 数据操作部分
# SQL语句书写
repo_sql = """select * from pr_repo"""
pr_sql = """
select 
pr_number,
created_at,
updated_at,
closed_at,
merged_at,
pr_user_name,
labels,
state
 from pr_self"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_get_labels()
# 关闭数据库连接
database.close()

import csv
import math
import pymysql as db
import requests

from utils.date_utils.date_function import project_age, get_waiting_time, is_weekday_commit, get_latency_after_response, \
    get_close_pr_time
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json




def test_get_close_pr_time():
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
    re_dict=get_close_pr_time(time_dict)
    print(re_dict)
    headers = ['pr_number',
               'time_dif'
               ]
    occure_time_dict={}
    with open(
            "E:\\pythonProject\\nju_pr_project\\utils\\date_utils\\test\\angular.js_time_dif_result.csv",
            'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in re_dict.keys():
            str_temp=[]
            str_temp.append(item)
            str_temp.append(re_dict[item])
            temp_int=int((re_dict[item]/60)/24+1)
            if occure_time_dict.__contains__(temp_int):
                occure_time_dict[temp_int]=occure_time_dict.get(temp_int)+1
            else:
                occure_time_dict[temp_int]=1
            writer.writerow(str_temp)
    headers = ['time_dif',
               'appear_time'
               ]
    with open(
            "E:\\pythonProject\\nju_pr_project\\utils\\date_utils\\test\\angular.js_time_dif_occure_time_result.csv",
            'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in occure_time_dict.keys():
            str_temp = []
            str_temp.append(item)
            str_temp.append(occure_time_dict[item])
            writer.writerow(str_temp)


# 数据操作部分
# SQL语句书写
pr_sql = """select pr_number,created_at,updated_at,closed_at,merged_at,comments_number,comments_content,review_comments_number,review_comments_content,pr_user_name 
            from pr_self
            where repo_name='angular.js' and closed_at is not null 
            order by pr_number
            """
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_get_close_pr_time()
# 关闭数据库连接
database.close()

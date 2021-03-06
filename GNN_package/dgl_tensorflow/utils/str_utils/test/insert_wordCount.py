import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
from utils.str_utils.str_function import getBody, wordCount, wordCount_list
import traceback
import time
import json

# 数据操作部分
# SQL语句书写
sql = """SELECT pr_number,body,title,comments_content,review_comments_content FROM `pr_self` """
update_sql = """UPDATE pr_self SET body_word_count=%s,title_length=%s,comments_word_count=%s WHERE pr_number=%s"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='asd159357', db='third_pr', charset='utf8mb4')
# 创建游标对象
cursor = database.cursor()
database.ping(reconnect=True)

try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        pr_number = row[0]
        body = row[1]
        title = row[2]
        comments_json = json.loads(row[3])
        review_comments_json = json.loads(row[4])

        comments = getBody(comments_json)
        review_comments = getBody(review_comments_json)

        body_word_count = wordCount(body)
        title_length = wordCount(title)
        comments_word_count = wordCount_list(comments) + wordCount_list(review_comments)
        print(comments)
        print(review_comments)
        print(body_word_count.__str__() + ' ' + title_length.__str__() + ' ' + comments_word_count.__str__())
        try:
            # 将计算数据放入数据库
            sqlData = (body_word_count, title_length, comments_word_count, pr_number)
            database.ping(reconnect=True)
            cursor.execute(update_sql, sqlData)
            # 提交到数据库执行
            database.commit()
            print("第", pr_number, "行数据更新到数据库成功: ")
        except Exception as e:
            # 如果发生错误则回滚
            print("第", pr_number, "行数据插入数据库失败: ")
            print(e)
            # traceback.print_exc()
            database.ping(reconnect=True)
            database.rollback()
            break
except Exception as e:
    print(e)
# 打印结果
# print(results)
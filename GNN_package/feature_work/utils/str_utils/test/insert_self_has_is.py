import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
from utils.str_utils.str_function_self import has_text, is_text, responded
import traceback
import time
import json

# 数据操作部分
# SQL语句书写
sql = """SELECT pr_number,pr_user_id,body,pr_author_association,review_comments_number,review_comments_content FROM `pr_self`"""
update_sql_self = """UPDATE pr_self SET 
                is_contributor=%s,
                is_core_member=%s,
                is_responded=%s,
                is_reviewer=%s,
                has_bug=%s,
                has_document=%s,
                has_feature=%s,
                has_improve=%s,
                has_refactor=%s,
                Has_Test_Code=%s,
                at_mention=%s 
                WHERE pr_number=%s"""

sql_user = """SELECT user_id,author_association_with_repo FROM pr_user WHERE user_id<5000"""
update_sql_self = """UPDATE pr_self SET 
                is_contributor=%s,
                is_core_member=%s,
                is_responded=%s,
                is_reviewer=%s,
                has_bug=%s,
                has_document=%s,
                has_feature=%s,
                has_improve=%s,
                has_refactor=%s,
                Has_Test_Code=%s,
                at_mention=%s 
                WHERE pr_number=%s"""
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
        num = 0
        pr_number = row[0]
        pr_user_id = row[1]
        body = row[2]
        pr_author_association = row[3]
        review_comments_number = row[4]
        review_comments_json = json.loads(row[5])

        is_responded = responded(num, review_comments_json, pr_user_id)

        is_list = is_text(pr_author_association)

        has_list = has_text(body)

        try:
            # 将计算数据放入数据库
            sqlData_self = (
                is_list[0], is_list[1], is_responded, is_list[2], has_list[0], has_list[1], has_list[2],
                has_list[3], has_list[4],
                has_list[5], has_list[6], pr_number)
            database.ping(reconnect=True)
            cursor.execute(update_sql_self, sqlData_self)
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
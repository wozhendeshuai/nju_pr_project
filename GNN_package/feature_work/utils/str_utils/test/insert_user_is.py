import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
from utils.str_utils.str_function_user import is_text
import traceback
import time
import json

sql="""SELECT user_id,author_association_with_repo FROM pr_user"""
update_sql_user="""UPDATE pr_user SET 
                is_contributor=%s,
                is_core_member=%s,
                is_reviewer=%s 
                WHERE user_id=%s"""

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
        user_id = row[0]
        author_association_json = json.loads(row[1])
        author_association=author_association_json["tensorflow"]
        print(author_association)

        is_list=is_text(author_association)

        try:
           #将计算数据放入数据库
           sqlData_user=(is_list[0],is_list[1],is_list[2],user_id)
           database.ping(reconnect=True)
           cursor.execute(update_sql_user, sqlData_user)
           # 提交到数据库执行
           database.commit()
           print("第", user_id, "行数据更新到数据库成功: ")
        except Exception as e:
           # 如果发生错误则回滚
           print("第", user_id, "行数据插入数据库失败: ")
           print(e)
           # traceback.print_exc()
           database.ping(reconnect=True)
           database.rollback()
           break
except Exception as e:
    print(e)
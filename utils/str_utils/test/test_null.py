import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
import traceback
import time
import json

# 数据操作部分
# SQL语句书写
sql = """SELECT pr_number,pr_user_id,body,pr_author_association,review_comments_number,review_comments_content FROM `pr_self` where pr_number=6049"""
update_sql_self="""UPDATE pr_self SET 
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
                WHERE pr_number=6049"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='asd159357', db='third_pr', charset='utf8mb4')
# 创建游标对象
cursor = database.cursor()
database.ping(reconnect=True)
#获取review——content中的所有id

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

        #判断is_responded，剔除自己review自己
        for i in range(0, len(review_comments_json)):
            print(review_comments_json)
            print(i)
            if review_comments_json[i]["user"] is None:
                continue
            print(review_comments_json[i]["user"]["id"])
            review_comments_content_id = review_comments_json[i]["user"]["id"]

            if review_comments_content_id!=pr_user_id:
                num = num+1
        if num > 0:
            is_responded = 1
        else:
            is_responded = 0

        #判断is_contributor、is_core_member、is_reviewer
        is_contributor = 0
        is_core_member = 0
        is_reviewer = 0
        if pr_author_association == "CONTRIBUTOR":
            is_contributor = 1
        elif pr_author_association == "MEMBER":
            is_core_member = 1
        elif pr_author_association == "REVIEWER":
            is_reviewer = 1
        else:
            print("NONE")
        print(pr_author_association)
        print(is_contributor)
        #判断has_bug、has_document、has_feature、has_improve、has_refactor、Has_Test_Code、at_mention
        has_bug = 0
        has_document = 0
        has_feature = 0
        has_improve = 0
        has_refactor = 0
        Has_Test_Code = 0
        at_mention = 0
        if body is None:
            print("body为空")
        else:
            if "bug" in body:
                has_bug = 1
            if "document" in body:
                has_document = 1
            if "feature" in body:
                has_feature = 1
            if "improve" in body:
                has_improve = 1
            if "refactor" in body:
                has_refactor = 1
            if "test" in body:
                Has_Test_Code = 1
            if "@" in body:
                at_mention = 1
        try:
           #将计算数据放入数据库
           sqlData_self=(is_contributor,is_core_member,is_responded,is_reviewer,has_bug,has_document,has_feature,
                    has_improve,has_refactor,Has_Test_Code,at_mention)
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
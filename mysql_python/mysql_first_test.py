import pymysql as db
import datetime
import requests

# 链接数据库
from utils.time_utils import time_reverse

database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='test_pr_first', charset='utf8')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute('select version()')
data = cursor.fetchone()
print(data)

# 调用api接口
url = 'https://api.github.com/repos/nodejs/node/pulls/40371'

r = requests.get(url)
# 打印下看看
print("Status Code:", r.status_code)
json_str = r.json()
print(json_str)
print('r body: ', r.json()['body'])
print('json body: ', json_str['body'])
print('json pr_number: ', json_str['number'])
print('json pr_url: ', json_str['url'])
print('json pr_user_id: ', json_str['user']['id'])
print('json pr_user_name: ', json_str['user']['login'])
print('json created_at: ', json_str['created_at'])
print('json updated_at: ', json_str['updated_at'])
print('json close_at: ', json_str['closed_at'])
print('json mergeable: ', ((json_str['mergeable'] == True) and 1 or 0))
print('json merged_at: ', json_str['merged_at'])
print('json merged: ', json_str['merged'])
print('json comments_number: ', json_str['comments'])

create_time = json_str['created_at'].replace('T', ' ')
create_time = create_time.replace('Z', '')
print(create_time)
print('json created_at: ', time_reverse(json_str['created_at']))
# SQL语句书写
sql = """INSERT INTO nodejs_pr_test(
         pr_number,
         pr_url,
         pr_user_id,
         pr_user_name,
         created_at,
         updated_at,
         close_at,
         mergeable,
         merged_at,
         merged,
         comments_number)
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
sqlData = (
    json_str['number']
    , json_str['url']
    , json_str['user']['id']
    , json_str['user']['login']
    , time_reverse(json_str['created_at'])
    , time_reverse(json_str['updated_at'])
    , time_reverse(json_str['closed_at'])
    , ((json_str['mergeable'] == True) and 1 or 0)
    , time_reverse(json_str['merged_at'])
    , ((json_str['merged'] == True) and 1 or 0)
    , json_str['comments'])
# 执行SQL
cursor.execute(sql, sqlData)

database.commit()

'''
try:
    # 执行sql语句
    cursor.execute(sql,sqlData)
    # 提交到数据库执行
    database.commit()
except:
    # 如果发生错误则回滚
    print("失败",json_str['number'] )
    database.rollback()
'''
# 关闭数据库连接
database.close()

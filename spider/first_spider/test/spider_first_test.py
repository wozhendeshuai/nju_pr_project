import pymysql as db

import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token

repo_name = 'nodejs/node'
# 调用api接口
url = 'https://api.github.com/repos/' + repo_name + '/pulls/40370'
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
r = requests.get(url, headers=headers)

print("Status Code:", r.status_code)
print('status header', r.headers)
print(r.json())
json_str = r.json()
print(json_str)
print('pr_r body: ', r.json()['body'])
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
print('json is_merged: ', json_str['merged'])
print('json comments_number: ', json_str['comments'])
print('json pr_body: ', json_str['body'])
print('json pr_file_edit_num: ', json_str['changed_files'])
print('json pr_line_add_num: ', json_str['additions'])
print('json pr_line_del_num: ', json_str['deletions'])
print('json commits_num: ', json_str['commits'])
create_time = json_str['created_at'].replace('T', ' ')
create_time = create_time.replace('Z', '')
print(create_time)
print('json created_at: ', time_reverse(json_str['created_at']))

# 数据操作部分
# SQL语句书写
sql = """INSERT INTO nodejs_pr_test(
         pr_number,
         pr_url,
         repo_name,
         pr_user_id,
         pr_user_name,
         created_at,
         updated_at,
         close_at,
         is_merged,
         merged_at,
         mergeable,
         comments_number,
         pr_body,
         pr_file_edit_num,
         pr_line_add_num,
         pr_line_del_num,
         commits_num)
         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
sqlData = (
    json_str['number']
    , json_str['url']
    , repo_name
    , json_str['user']['id']
    , json_str['user']['login']
    , time_reverse(json_str['created_at'])
    , time_reverse(json_str['updated_at'])
    , time_reverse(json_str['closed_at'])
    , ((json_str['mergeable'] == True) and 1 or 0)
    , time_reverse(json_str['merged_at'])
    , ((json_str['merged'] == True) and 1 or 0)
    , json_str['comments']
    , json_str['body']
    , json_str['changed_files']
    , json_str['additions']
    , json_str['deletions']
    , json_str['commits'])
# #执行SQL
# cursor.execute(sql,sqlData)
#
# database.commit()

# 链接数据库


database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='test_pr_first', charset='utf8')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute('select version()')
data = cursor.fetchone()

print(data)
try:
    # 执行sql语句
    cursor.execute(sql, sqlData)
    # 提交到数据库执行
    database.commit()
    print("成功", json_str['number'])
except:
    # 如果发生错误则回滚
    print("失败", json_str['number'])
    database.rollback()

# 关闭数据库连接
database.close()

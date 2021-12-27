import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json

access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}

# 数据操作部分
# SQL语句书写
sql = """
    insert into pr_user(
    user_id, 
    user_name, 
    followers_num,
    followers, 
    following_num,
    following, 
    public_repos_num, 
    author_association_with_repo)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s )
   """
select_pr_user_sql = """
       		
    SELECT  user_id, user_name,author_association_with_repo
	from pr_user
	where user_name=%s
	"""
updata_sql = "UPDATE pr_user SET author_association_with_repo = %s WHERE user_id = %s"

pr_user_url = "https://api.github.com/users/"
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8mb4')
# 创建游标对象
cursor = database.cursor()
sqldata = "kashif"
# 利用游标对象进行操作
cursor.execute(select_pr_user_sql, sqldata)
data = cursor.fetchall()
print(data)
data_len = data.__len__()
index = 0
while index < data_len:
    # 取出查询的数据
    user_id = data[index][0]
    user_name = data[index][1]
    author_association_with_repo = json.loads(data[index][2])
    author_association_with_repo["asd"] = "asd222"
    val = (json.dumps(author_association_with_repo), user_id)
    cursor.execute(updata_sql, val)
    print()
    database.commit()

    index = index + 1

# 关闭数据库连接
database.close()

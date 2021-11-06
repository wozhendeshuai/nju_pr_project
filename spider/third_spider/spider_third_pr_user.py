import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json

'''
此处需要注意，这里的author_association_with_repo，当一个用户在多个代码仓都有提交的时候，我们需要把author_association_with_repo取出来
然后再加入新的内容
测试代码在spider/third_spider/test/test.py
'''


# 根据url以及url中蕴含的数来取
def url_to_json(url, number):
    url_str = url + "?per_page=100&anon=true&page="
    print(url_str)
    page = 1
    maxPage = number // 100 + 1
    count = 0
    re_json = json.loads("[]")
    while page <= maxPage:
        temp_url_str = url_str + page.__str__()
        print(temp_url_str)
        url_r = requests.get(temp_url_str, headers=headers)
        re_json = re_json + url_r.json()
        page = page + 1
    return re_json


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
select_pr_self_sql = """
   	SELECT DISTINCT(pr_user_id),pr_user_name,pr_author_association,repo_name
	from pr_self
	order by pr_user_id
	"""
# 查询是否在之前的仓库取数据时，已经爬取该用户的数据
select_pr_user_sql = """
   	SELECT  user_id, user_name,author_association_with_repo
	from pr_user
	where user_name=%s
	"""
# 用于更新author_association_with_repo数据
updata_sql = "UPDATE pr_user SET author_association_with_repo = %s WHERE user_id = %s"
pr_user_url = "https://api.github.com/users/"
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8mb4')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute(select_pr_self_sql)
data = cursor.fetchall()
print(data)
data_len = data.__len__()
index = 0
while index < data_len:
    # 取出查询的数据
    pr_user_id = data[index][0]
    pr_user_name = data[index][1]
    author_association_with_repo = data[index][2]
    repo_name = data[index][3]
    print("========================" + "第" + str(index) + "号 user: " + str(
        pr_user_name) + "==========================")
    print(pr_user_id)
    print(pr_user_name)
    print(author_association_with_repo)
    print(repo_name)
    try:
        # 利用游标对象进行操作
        cursor.execute(select_pr_user_sql, pr_user_name)
        pr_user_data = cursor.fetchall()
        if pr_user_data.__len__() == 0:
            # 拼接url
            temp_pr_url = pr_user_url + pr_user_name
            print(temp_pr_url)
            temp_pr_url_r = requests.get(temp_pr_url, headers=headers)
            print("temp_pr_url: " + temp_pr_url + "  Status Code:", temp_pr_url_r.status_code)
            user_json = temp_pr_url_r.json()
            followers_num = user_json["followers"]
            followers_url = user_json["followers_url"]
            followers_json = url_to_json(followers_url, followers_num)
            following_num = user_json["following"]
            following_url = 'https://api.github.com/users/' + pr_user_name + '/following'
            following_json = url_to_json(following_url, following_num)
            public_repos_num = user_json["public_repos"]
            relation = {}
            relation[repo_name] = author_association_with_repo
            author_association_with_repo_json = json.dumps(relation)
            try:
                sqlData = (
                    pr_user_id,
                    pr_user_name,
                    followers_num,
                    json.dumps(followers_json),
                    following_num,
                    json.dumps(following_json),
                    public_repos_num,
                    author_association_with_repo_json)
                # 执行sql语句
                cursor.execute(sql, sqlData)
                # 提交到数据库执行
                database.commit()
                print("第" + str(index) + "号 user: " + str(pr_user_name) + "数据插入成功")

            except Exception as e:
                # 如果发生错误则回滚
                print("第" + str(index) + "号 user: " + str(pr_user_name) + "数据插入数据库失败: " + str(e))
                # 当出现重复key时应当可以继续往下走，取下一条数据
                if e.args[0] == 1062 or e.args[1].__contains__("Duplicate"):
                    index = index + 1
                    continue
                filename = 'pr_user_exception.csv'
                write_file(index, "user", ("第" + str(index) + "号 user: " + str(pr_user_name) + "数据插入数据库失败: " + str(e)),
                           filename)
                print(e)
                traceback.print_exc()
                database.rollback()
                break
        elif pr_user_data.__len__() == 1:
            user_id = pr_user_data[index][0]
            user_name = pr_user_data[index][1]
            author_association_with_repo = json.loads(pr_user_data[index][2])
            if author_association_with_repo.__contains__(repo_name):
                continue
            else:
                author_association_with_repo[repo_name] = author_association_with_repo
                val = (json.dumps(author_association_with_repo), user_id)
                cursor.execute(repo_name, val)
                database.commit()
        else:
            print("第" + str(index) + "号 user: " + str(pr_user_name) + " 用户信息异常: " + str(pr_user_data.__len__()))
    except Exception as e:
        # 如果发生错误则回滚
        print("第" + str(index) + "号 user: " + str(pr_user_name) + " 失败: " + str(e))
        filename = 'pr_user_file_exception.csv'
        write_file(index, "user", ("第" + str(index) + "号 user: " + str(pr_user_name) + " 失败: " + str(e)), filename)
        print(e)
        # traceback.print_exc()
        database.rollback()
        break

    index = index + 1

# 关闭数据库连接
database.close()

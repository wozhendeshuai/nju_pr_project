import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time


def find_min_time(pr_user_id, pr_user_name, comments_json):
    if comments_json.__len__() == 0:
        return None
    comment_time = None
    comment_user = pr_user_name
    comment_user_id = pr_user_id
    for i in range(0, comments_json.__len__()):
        if comments_json[i]["user"]["login"].__eq__(pr_user_name) and comments_json[i]["user"]["id"].__eq__(pr_user_id):
            continue
        elif comment_time == None:
            comment_user = comments_json[i]["user"]["login"]
            comment_user_id = comments_json[i]["user"]["id"]
            comment_time = comments_json[i]["created_at"]
        else:
            if comment_time > comments_json[i]["created_at"]:
                comment_user = comments_json[i]["user"]["login"]
                comment_user_id = comments_json[i]["user"]["id"]
                comment_time = comments_json[i]["created_at"]
    return comment_time, comment_user, comment_user_id


owner_name = "nodejs"
repo_name = "node"
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
# 数据操作部分
# 查询SQL语句书写
select_sql = """
SELECT pr_number
from nodejs_pr_test
order by pr_number
"""
# 初始化一下
comment_time, comment_user, comment_user_id = None, None, None
review_comment_time, review_comment_user, review_comment_user_id = None, None, None
final_comment_time, final_comment_user, final_comment_user_id = None, None, None
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='test_pr_first', charset='utf8')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute(select_sql)
data = cursor.fetchall()
print(data)
data_len = data.__len__()
index_id = 0
while index_id < data_len:
    # 调用api接口
    pr_number = data[index_id][0]
    print("pr_number", pr_number)
    pr_url = 'https://api.github.com/repos/' + owner_name + '/' + repo_name + '/pulls/' + str(pr_number)
    try:
        pr_r = requests.get(pr_url, headers=headers)
        print("pr_url: " + pr_url + "  Status Code:", pr_r.status_code)
    except Exception as e:
        # 如果发生错误则回滚
        print("网络连接失败: ", pr_url)
        filename = repo_name + '_PR_network_exception.csv'
        write_file(index_id, repo_name, str(pr_number) + str(e) + pr_url, filename)
        print(e)
        time.sleep(7)
        continue
    # 如果返回的状态码以2开头，则说明正常此时去写入到数据库中即可
    if pr_r.status_code >= 200 and pr_r.status_code < 300:
        pr_json = pr_r.json()
        pr_user_id = pr_json['user']['id']
        pr_user_name = pr_json['user']['login']

        # 获取评论相关信息
        comments_url = pr_json["_links"]["comments"]["href"]
        comments_r = requests.get(comments_url, headers=headers)
        comments_json = comments_r.json()
        if comments_json.__len__() > 0:
            comment_time, comment_user, comment_user_id = find_min_time(pr_user_id, pr_user_name, comments_json)

        # 获取评审评论相关信息
        review_comments_url = pr_json["_links"]["review_comments"]["href"]
        review_comments_r = requests.get(review_comments_url, headers=headers)
        review_comments_json = review_comments_r.json()
        if review_comments_json.__len__() > 0:
            review_comment_time, review_comment_user, review_comment_user_id = find_min_time(pr_user_id, pr_user_name,
                                                                                             comments_json)
        #将获取得到的数据进行相应的存储
        if review_comment_time is not None and comment_time is not None:
            if review_comment_time > comment_time:
                final_comment_time, final_comment_user, final_comment_user_id = comment_time, comment_user, comment_user_id
            else:
                final_comment_time, final_comment_user, final_comment_user_id = review_comment_time, review_comment_user, review_comment_user_id
        elif review_comment_time is None and comment_time is None:
            final_comment_time, final_comment_user, final_comment_user_id = None, None, None
        else:
            if review_comment_time is not None:
                final_comment_time, final_comment_user, final_comment_user_id = review_comment_time, review_comment_user, review_comment_user_id
            else:
                final_comment_time, final_comment_user, final_comment_user_id = comment_time, comment_user, comment_user_id
    else:
        filename = repo_name + '_PRNumbers_exception.csv'
        write_file(index_id, repo_name, str(pr_number) + pr_r.status_code.__str__() + str(pr_r.json()), filename)
# 关闭数据库连接
database.close()

'''
index = 20000

# print(data)
while index < 20001:
    #
    sqlData = (
            json_str['number']
            , json_str['url']
            , owner_name + "/" + repo_name
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
        try:
            # 执行sql语句
            cursor.execute(sql, sqlData)
            # 提交到数据库执行
            database.commit()
            print("插入数据库成功: ", json_str['number'])
        except Exception as e:
            # 如果发生错误则回滚
            print("插入数据库失败: ", url + "  " + str(json_str['number']))
            filename = repo_name + '_PR_database_operation_exception.csv'
            write_file(index, repo_name, str(e), filename)
            print(e)
            # traceback.print_exc()
            database.rollback()
    # 如果返回的状态码有问题，则按照问题去处理一下，记录到文件中
  

   
'''

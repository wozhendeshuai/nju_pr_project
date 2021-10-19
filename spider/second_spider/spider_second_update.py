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
exception_filename = repo_name + '_comment_exception.csv'
# 数据操作部分
# 查询SQL语句书写
select_sql = """SELECT pr_number from nodejs_pr_test order by pr_number
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
    print("==============", index_id.__str__(), "==================")
    # 调用api接口
    pr_number = data[index_id][0]
    print("index_id: " + str(index_id) + "pr_number", pr_number)
    pr_url = 'https://api.github.com/repos/' + owner_name + '/' + repo_name + '/pulls/' + str(pr_number)
    try:
        pr_r = requests.get(pr_url, headers=headers)
        print("index_id: " + str(index_id) + "pr_url: " + pr_url + "  Status Code:", pr_r.status_code)
    except Exception as e:
        # 如果发生错误则回滚
        print("index_id: " + str(index_id) + "网络连接失败: ", pr_url)
        write_file(index_id, repo_name,
                   "index_id: " + str(index_id) + " pr_number: " + str(pr_number) + str(e) + pr_url,
                   exception_filename)
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
            print("comment_time, comment_user, comment_user_id:", comment_time, comment_user, comment_user_id)

        # 获取评审评论相关信息
        review_comments_url = pr_json["_links"]["review_comments"]["href"]
        review_comments_r = requests.get(review_comments_url, headers=headers)
        review_comments_json = review_comments_r.json()
        if review_comments_json.__len__() > 0:
            review_comment_time, review_comment_user, review_comment_user_id = find_min_time(pr_user_id, pr_user_name,
                                                                                             comments_json)
            print("review_comment_time, review_comment_user, review_comment_user_id :", review_comment_time,
                  review_comment_user, review_comment_user_id)
        # 将获取得到的数据进行相应的存储
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
        print("index_id: " + str(index_id), final_comment_time, final_comment_user, final_comment_user_id)

        try:
            updata_sql = "UPDATE nodejs_pr_test SET pr_author_association = %s,first_comment_time = %s,first_comment_member_id = %s,first_comment_member_name = %s WHERE pr_number = %s"
            val = (
                pr_json["author_association"], time_reverse(final_comment_time), final_comment_user_id,
                final_comment_user,
                pr_number)
            cursor.execute(updata_sql, val)
            database.commit()
            print(index_id, " 条记录已更新", "pr_number: ", pr_number)
        except Exception as e:
            # 如果发生错误则回滚
            print(index_id, " 条记录插入数据库失败", "pr_number: ", pr_number)
            filename = repo_name + '_PR_database_operation_exception.csv'
            write_file(index_id, repo_name, "index_id: " + str(index_id) + " pr_number: " + str(pr_number) + str(e),
                       filename)
            print(e)
            # traceback.print_exc()
            database.rollback()
            continue

        # 成功执行继续下一个
        index_id = index_id + 1
    else:
        write_file(index_id, repo_name,
                   "index_id: " + str(index_id) + " pr_number: " + str(pr_number) + pr_r.status_code.__str__() + str(
                       pr_r.json()), exception_filename)
    continue
# 关闭数据库连接
database.close()

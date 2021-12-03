import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
import traceback
import time
import json
#test_branch
#test_branch
#test_branch
#test_branch
# 此部分可修改，用于控制进程，与爬取的仓库
index = 0
maxNum = 28900 #需根据具体的来自定义
owner_name ="spring-projects"#"symfony"#"rails"#"angular" #"tensorflow"
repo_name ="spring-boot" #"symfony"#"rails"#"angular.js"#"tensorflow"
# https://api.github.com/repos/tensorflow/tensorflow/pulls/872
# 获取token todo：可以进行选择，不然这样一直是一个会有限制
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
# repo url拼接
pr_url = "https://api.github.com/repos/" + owner_name + "/" + repo_name + "/pulls/"

print(pr_url)

# 数据操作部分
# SQL语句书写
sql = """INSERT into pr_self(
    pr_number,
    pr_url,
    repo_name,
    pr_user_id,
    pr_user_name,
    pr_author_association,
    title,
    body,
    labels,
    state,
    created_at,
    updated_at,
    closed_at,
    merged_at,
    merged,
    mergeable,
    mergeable_state,
    merge_commit_sha,
    assignees_content,
    requested_reviewers_content,
    comments_number,
    comments_content,
    review_comments_number,
    review_comments_content,
    commit_number,
    commit_content,
    changed_file_num,
    total_add_line,
    total_delete_line
    )VALUES(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s, %s,%s, %s,%s, %s, %s,%s,%s,%s, %s,%s,%s,%s, %s, %s,%s,%s,%s,%s)"""

# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8mb4')
# 创建游标对象
cursor = database.cursor()
database.ping(reconnect=True)


# 统计url中含有的元素数量
def findUrlJsonCount(url_str):
    url_str = url_str + "?per_page=100&anon=true&page="
    # print(url_str)
    page = 1
    count = 0
    while 1:
        temp_url_str = url_str + page.__str__()
        print(temp_url_str)
        url_r = requests.get(temp_url_str, headers=headers)
        url_json = url_r.json()
        if len(url_json) < 100:
            count = count + len(url_json)
            return count
        else:
            count = count + 100
            page = page + 1
    return count


def list_to_json(temp_list):
    dict = {}
    for i in range(0, temp_list.__len__()):
        dict[i] = temp_list[i]

    return json.dumps(dict)


# 根据评论条数来取
def url_to_json(url, number):
    url_str = url + "?per_page=100&anon=true&page="
    # print(url_str)
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


while index < maxNum:
    try:
        print("========================" + "第" + str(index) + "号 pr_number: " + str(
            index) + "信息保存中==========================")
        temp_url = pr_url + index.__str__()
        pr_r = requests.get(temp_url, headers=headers)
        print("pr_url: " + temp_url + "  Status Code:", pr_r.status_code)
    except Exception as e:
        # 如果发生错误则回滚
        print("网络连接失败: pr_url: ", temp_url)
        filename = repo_name + '_exception.csv'
        write_file(index, repo_name + "-" + owner_name,
                   str(e) + ("网络连接失败: pr_url: " + temp_url + "  Status Code:", pr_r.status_code),
                   filename)
        print(e)
        time.sleep(10)
        continue
    # 如果返回的状态码以2开头，则说明正常此时去写入到数据库中即可
    if pr_r.status_code >= 200 and pr_r.status_code < 300:
        pr_json_str = pr_r.json()
        # print("len(pr_json_str):", len(pr_json_str))
        # 基础数据
        pr_number = index
        pr_user_id = pr_json_str["user"]["id"]
        pr_user_name = pr_json_str["user"]["login"]
        pr_author_association = pr_json_str["author_association"]
        title = pr_json_str["title"]
        body = pr_json_str["body"]
        state = pr_json_str["state"]
        created_at = pr_json_str["created_at"]
        updated_at = pr_json_str["updated_at"]
        closed_at = pr_json_str["closed_at"]
        merged_at = pr_json_str["merged_at"]
        merged = pr_json_str["merged"]
        mergeable = pr_json_str["mergeable"]
        mergeable_state = pr_json_str["mergeable_state"]
        merge_commit_sha = pr_json_str["merge_commit_sha"]
        comments_number = pr_json_str["comments"]
        review_comments_number = pr_json_str["review_comments"]
        commit_number = pr_json_str["commits"]
        changed_file_num = pr_json_str["changed_files"]
        total_add_line = pr_json_str["additions"]
        total_delete_line = pr_json_str["deletions"]
        # json统一处理
        labels = list_to_json(pr_json_str["labels"])
        assignees_content = list_to_json(pr_json_str["assignees"])
        requested_reviewers_content = list_to_json(pr_json_str["requested_reviewers"])
        comments_content = url_to_json(pr_json_str["comments_url"], comments_number)
        review_comments_content = url_to_json(pr_json_str["review_comments_url"], review_comments_number)
        commit_content = url_to_json(pr_json_str["commits_url"], commit_number)
        # 如果返回的状态码有问题，则按照问题去处理一下，记录到文件中
    else:
        filename = repo_name + '_exception.csv'
        write_file(index, repo_name, pr_r.status_code.__str__() + str(pr_r.json()), filename)
        index = index + 1
        continue
    try:
        sqlData = (
            pr_number,
            temp_url,
            repo_name,
            pr_user_id,
            pr_user_name,
            pr_author_association,
            title,
            body,
            labels,
            state,
            time_reverse(created_at),
            time_reverse(updated_at),
            time_reverse(closed_at),
            time_reverse(merged_at),
            ((merged == True) and 1 or 0),
            ((mergeable == True) and 1 or 0),
            mergeable_state,
            merge_commit_sha,
            assignees_content,
            requested_reviewers_content,
            comments_number,
            json.dumps(comments_content),
            review_comments_number,
            json.dumps(review_comments_content),
            commit_number,
            json.dumps(commit_content),
            changed_file_num,
            total_add_line,
            total_delete_line)
        database.ping(reconnect=True)
        # 执行sql语句
        cursor.execute(sql, sqlData)
        # 提交到数据库执行
        database.commit()
        print("第", index, "行数据插入数据库成功: ", repo_name)
        index = index + 1
    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行数据插入数据库失败: ", "repo_name:", repo_name)
        filename = repo_name + '_exception.csv'
        if e.args[0] == 1062 or e.args[1].__contains__("Duplicate"):
            index = index + 1
            continue
        write_file(index, "user",
                   ("第" + str(index) + "行数据插入数据库失败: " + "repo_name:" + repo_name + " " + str(e)),
                   filename)
        print(e)
        # traceback.print_exc()
        database.ping(reconnect=True)
        database.rollback()
        break
# 关闭数据库连接
database.close()

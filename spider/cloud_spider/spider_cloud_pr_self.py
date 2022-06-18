import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.exception_handdle import write_file
import time
import json


def list_to_json(temp_list):
    dict = {}
    for i in range(0, temp_list.__len__()):
        dict[i] = temp_list[i]

    return json.dumps(dict)


# 根据评论条数来取
def url_to_json(url, number, headers):
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


# 统计url中含有的元素数量
def findUrlJsonCount(url_str, headers):
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


# 封装成一个方法，让他方便外部调用
def get_pr_self_info(index, max_num, owner_name, repo_name, headers):
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
    update_sql = """update pr_self set
            pr_user_id=%s,
            pr_user_name=%s,
            pr_author_association=%s,
            title=%s,
            body=%s,
            labels=%s,
            state=%s,
            created_at=%s,
            updated_at=%s,
            closed_at=%s,
            merged_at=%s,
            merged=%s,
            mergeable=%s,
            mergeable_state=%s,
            merge_commit_sha=%s,
            assignees_content=%s,
            requested_reviewers_content=%s,
            comments_number=%s,
            comments_content=%s,
            review_comments_number=%s,
            review_comments_content=%s,
            commit_number=%s,
            commit_content=%s,
            changed_file_num=%s,
            total_add_line=%s,
            total_delete_line=%s
            where  pr_number=%s and repo_name=%s"""
    # 链接云端数据库
    # database = db.connect(host='172.19.241.129', port=3306, user='root', password='root', db='pr_second',
    #                       charset='utf8')
    database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
    # 创建游标对象
    cursor = database.cursor()
    database.ping(reconnect=True)
    # 自动找到最大的pr_number
    select_max_index = """select * from pr_self where repo_name= %s and state='open' order by pr_number """
    cursor.execute(select_max_index, [repo_name])
    open_pr_dict = []
    had_data = cursor.fetchall()
    if had_data.__len__() != 0:
        for i in range(had_data.__len__()):
            open_pr_dict.append(had_data[i][0])
        open_pr_dict.sort()
        print(open_pr_dict[0])
        index = open_pr_dict[0] - 1
        print("pr_self============目前开放状态的PR已到index为=============" + str(index))

    while index < max_num:
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
            comments_content = url_to_json(pr_json_str["comments_url"], comments_number, headers)
            review_comments_content = url_to_json(pr_json_str["review_comments_url"], review_comments_number, headers)
            commit_content = url_to_json(pr_json_str["commits_url"], commit_number, headers)
            # 如果返回的状态码有问题，则按照问题去处理一下，记录到文件中
        else:
            filename = repo_name + '_exception.csv'
            write_file(index, repo_name, pr_r.status_code.__str__() + str(pr_r.json()), filename)
            index = index + 1
            continue
        try:
            if open_pr_dict.__contains__(index):
                update_sqlData = (
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
                    total_delete_line,
                    pr_number,
                    repo_name)
                database.ping(reconnect=True)
                # 执行sql语句
                cursor.execute(update_sql, update_sqlData)
                # 提交到数据库执行
                database.commit()
                print("第", index, "行数据更新数据库成功: ", repo_name)
                temp_max_index = index
                for i in range(open_pr_dict.__len__()):
                    if open_pr_dict[i] == index:
                        temp_max_index = i
                        break
                if temp_max_index == (open_pr_dict.__len__() - 1):
                    index = index + 1
                else:
                    index = open_pr_dict[temp_max_index + 1]
            else:
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
            if e.args[0] == 1062 or e.args[1].__contains__("Duplicate") or e.args[0] == 1366:
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

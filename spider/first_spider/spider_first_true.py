import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time

owner_name = "nodejs"
repo_name = "node"
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
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

# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='test_pr_first', charset='utf8')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute('select version()')
data = cursor.fetchone()

index = 6810

# print(data)
while index < 20001:
    print("\n===0.7秒一次哦===============" + str(index) + "====================================\n")
    #
    # 调用api接口
    # 调用api接口
    url = 'https://api.github.com/repos/' + owner_name + '/' + repo_name + '/pulls/' + index.__str__()
    try:
        r = requests.get(url ,headers=headers)
        print("url: " + url + "  Status Code:", r.status_code)
        index = index + 1
    except Exception as e:
        # 如果发生错误则回滚
        print("网络连接失败: ", url)
        filename = repo_name+'_PR_network_exception.csv'
        write_file(index, repo_name, str(e) + url, filename)
        print(e)
        time.sleep(7)
        continue

    # 如果返回的状态码以2开头，则说明正常此时去写入到数据库中即可
    if r.status_code >= 200 and r.status_code < 300:
        json_str = r.json()
        sqlData = (
            json_str['number']
            , json_str['url']
            , owner_name + "/" + repo_name
            , json_str['user']['id']
            , json_str['user']['login']
            , time_reverse(json_str['created_at'])
            , time_reverse(json_str['updated_at'])
            , time_reverse(json_str['closed_at'])
            , ((json_str['merged'] == True) and 1 or 0)
            , time_reverse(json_str['merged_at'])
            , ((json_str['mergeable'] == True) and 1 or 0)
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
    else:
        filename = repo_name + '_PRNumbers_exception.csv'
        write_file(index, repo_name, r.status_code.__str__() + str(r.json()), filename)
# 关闭数据库连接
database.close()

import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time

# 获取文件相关内容
filepath = "E:\\pythonProject\\nju_pr_project\\spider\\second_spider\\test\\user_name_and_id.csv"
user_name_and_id = open(filepath, 'pr_r')
temp_user_name_id = user_name_and_id.readlines()
id_name_dict = {}
user_name = "wozhendeshuai"
user_id = "node"
index = 0

# 数据操作部分
# SQL语句书写
sql = """INSERT INTO pr_user(
         user_id,
         user_name,
         user_following,
         user_followers)
         VALUES(%s,%s,%s,%s) """

# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='test_pr_first', charset='utf8')
# 创建游标对象
cursor = database.cursor()
# 利用游标对象进行操作
cursor.execute('select version()')
data = cursor.fetchone()
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}

for i in range(0, len(temp_user_name_id)):
    temp_val = temp_user_name_id[i]
    print(temp_val)
    # 此处是为了去除数据中相关多余的符号
    val = temp_val.split(",")
    user_id = val[0].replace("\"", "")
    user_name = val[1][:len(val[1]) - 1].replace("\"", "")
    id_name_dict[user_id] = user_name
    # 用于存储关注和被关注用户信息集合
    following_id_name_str = ""
    follower_id_name_str = ""

    # 获取该用户关注和被关注的集合url拼接
    following_url = 'https://api.github.com/users/' + user_name + '/following'
    # print("following_url", following_url)
    follower_url = 'https://api.github.com/users/' + user_name + '/followers'
    # print("follower_url", follower_url)
    # 调用接口，出错的话进行记录，然后直接跳过该条
    try:
        followering_r = requests.get(following_url, headers=headers)
        print("following_url: " + following_url + "  Status Code:", followering_r.status_code)
        follower_r = requests.get(follower_url, headers=headers)
        print("follower_url: " + follower_url + "  Status Code:", follower_r.status_code)
    except Exception as e:
        # 如果发生错误则回滚
        print("网络连接失败: user_name: ", user_name, "user_id: ", user_id)
        filename = 'user_network_exception.csv'
        write_file(index, user_id + "-" + user_name, str(e) + ("网络连接失败: user_name: "+ user_name+ "user_id: "+ user_id),
                   filename)
        print(e)
        time.sleep(10)
        continue

    try:
        # 如果返回的状态码以2开头，则说明正常此时去写入到数据库中即可
        if followering_r.status_code >= 200 and followering_r.status_code < 300:
            following_json_str = followering_r.json()
            length_following = len(following_json_str)
            print("length_following:", length_following)
            if length_following > 0:
                for num in range(0, length_following):
                    following_name = following_json_str[num]['login']
                    following_id = following_json_str[num]['id']
                    following_id_name_str = following_id_name_str + (str(following_id) + "-" + following_name + ";")
            # following无数据，记录到文件中
            else:
                filename = 'user_data_exception.csv'
                write_file(index, user_name,
                           followering_r.status_code.__str__() + " following none data ",
                           filename)
        # 如果返回的状态码有问题，则按照问题去处理一下，记录到文件中
        else:
            filename = 'user_data_exception.csv'
            write_file(index, user_name,
                       followering_r.status_code.__str__() + " following status ",
                       filename)
    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行 following 数据出现问题", "问题是: ", str(e))
        filename = 'user_data_exception.csv'
        write_file(index, user_name, ("第"+ str(index)+ "行数据出现问题"+ "问题是: "+ str(e)), filename)
        time.sleep(7)

    # 获取该关注该用户的集合
    try:
        if follower_r.status_code >= 200 and follower_r.status_code < 300:
            follower_json_str = follower_r.json()
            length_follower = len(follower_json_str)
            print("length_follower:",length_follower)
            if length_follower > 0:
                for num in range(0, length_follower):
                    follower_name = follower_json_str[num]['login']
                    follower_id = follower_json_str[num]['id']
                    follower_id_name_str = follower_id_name_str + (str(follower_id) + "-" + follower_name + ";")
                    # follower无数据，记录到文件中
                else:
                    filename = 'user_data_exception.csv'
                    write_file(index, user_name,
                               follower_r.status_code.__str__() + " follower none data",
                               filename)
            # 如果返回的状态码有问题，则按照问题去处理一下，记录到文件中
        else:
            filename = 'user_data_exception.csv'
            write_file(index, user_name,
                       follower_r.status_code.__str__() + " following status ",
                       filename)
    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行 follower 数据出现问题", "问题是: ", str(e))
        filename = 'user_data_exception.csv'
        write_file(index, user_name, ("第" + str(index) + "行数据出现问题" + "问题是: " + str(e)), filename)
        time.sleep(7)

    index = index + 1

    try:
        sqlData = (
            user_id
            , user_name
            , following_id_name_str
            , follower_id_name_str)
        # 执行sql语句
        cursor.execute(sql, sqlData)
        # 提交到数据库执行
        database.commit()
        print("第", index, "行数据插入数据库成功: ", user_name)
    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行数据插入数据库失败: ", "user_name:", user_name, "user_id:", user_id)
        filename = 'user_database_operation_exception.csv'
        write_file(index, "user",
                   ("第" + str(index) + "行数据插入数据库失败: " + "user_name:" + user_name + "user_id:" + user_id + str(e)),
                   filename)
        print(e)
        # traceback.print_exc()
        database.rollback()
    print("======================" + str(index) + "=========================")
# 关闭数据库连接
database.close()
print(len(id_name_dict))

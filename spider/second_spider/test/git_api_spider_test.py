import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time

filepath = "E:\\pythonProject\\nju_pr_project\\spider\\second_spider\\test\\user_name_and_id.csv"
user_name_and_id = open(filepath, 'r')
temp_user_name_id = user_name_and_id.readlines()
id_name_dict = {}
user_name = "wozhendeshuai"
user_id = "node"
index = 0
for i in range(0, len(temp_user_name_id)):
    print(i, "  ", temp_user_name_id[i])
    temp_val = temp_user_name_id[i]
    print(temp_val)
    # 此处是为了去除数据中相关多余的符号
    val = temp_val.split(",")
    user_id = val[0].replace("\"", "")
    user_name = val[1][:len(val[1]) - 1].replace("\"", "")
    id_name_dict[user_id] = user_name

    access_token = get_token()
    headers = {
        'Authorization': 'token ' + access_token
    }
    # 获取该用户关注的集合
    following_url = 'https://api.github.com/users/' + user_name + '/following'
    print(following_url)
    try:
        r = requests.get(following_url, headers=headers)
        print("url: " + following_url + "  Status Code:", r.status_code)
        print(r.json())
        following_json_str = r.json()
        print(len(following_json_str))
        length_following = len(following_json_str)
        following_id_name_str = ""
        if length_following > 0:
            for num in range(0, length_following):
                following_name = following_json_str[num]['login']
                following_id = following_json_str[num]['id']
                print(str(following_id) + "-" + following_name + ";")
                following_id_name_str = following_id_name_str + (str(following_id) + "-" + following_name + ";")

    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行数据出现问题", "网络连接失败: ", following_url)
        print(e)
        time.sleep(7)
    # 获取该关注该用户的集合
    follower_url = 'https://api.github.com/users/' + user_name + '/followers'
    print(follower_url)
    try:
        r = requests.get(follower_url, headers=headers)
        print("url: " + follower_url + "  Status Code:", r.status_code)
        print(r.json())
        follower_json_str = r.json()
        print(len(follower_json_str))
        length_follower = len(follower_json_str)
        follower_id_name_str = ""
        if length_follower > 0:
            for num in range(0, length_follower):
                follower_name = follower_json_str[num]['login']
                follower_id = follower_json_str[num]['id']
                print(str(follower_id) + "-" + follower_name + ";")
                follower_id_name_str = follower_id_name_str + (str(follower_id) + "-" + follower_name + ";")
    except Exception as e:
        # 如果发生错误则回滚
        print("第", index, "行数据出现问题", "网络连接失败: ", following_url)
        print(e)
        time.sleep(7)
    print("following_id_name_str", following_id_name_str)
    print("follower_id_name_str", follower_id_name_str)
    index = index + 1

print(len(id_name_dict))

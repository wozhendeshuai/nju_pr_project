import pymysql as db
import requests

from utils.date_utils.date_function import project_age, get_waiting_time, is_weekday_commit, get_latency_after_response
from utils.file_utils.file_function import get_file_type_num, get_file_directory_num, get_segs_added_num, \
    get_segs_deleted_num, get_segs_updated_num, get_test_inclusion, get_subsystem_num, get_language_num, \
    get_changes_files_modified_num, get_file_developer_num, get_file_developer_change_num, \
    get_file_developer_recent_change_num
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time
import json


def test_directory_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    # for key in file_dict.keys():
    #     print("key: "+str(key))
    #     print("file_name:  "+file_dict[key].__str__())
    file_directory_num = get_file_directory_num(file_dict)
    for key in file_directory_num.keys():
        print("key: " + str(key) + "     file_directory_num:  " + file_directory_num[key].__str__())


def test_language_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    # for key in file_dict.keys():
    #     print("key: "+str(key))
    #     print("file_name:  "+file_dict[key].__str__())
    language_num = get_language_num(file_dict)
    for key in language_num.keys():
        print("key: " + str(key) + "   language_num:  " + language_num[key].__str__())


def test_file_type_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    # for key in file_dict.keys():
    #     print("key: "+str(key))
    #     print("file_name:  "+file_dict[key].__str__())
    file_type_num = get_file_type_num(file_dict)
    for key in file_type_num.keys():
        print("key: " + str(key) + "   fileTypeNum:  " + file_type_num[key].__str__())


def test_segs_added_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    file_segs_added_num = get_segs_added_num(file_dict)
    for key in file_segs_added_num.keys():
        print("key: " + str(key) + "   file_segs_added_num:  " + file_segs_added_num[key].__str__())


def test_segs_deleted_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    file_segs_deleted_num = get_segs_deleted_num(file_dict)
    for key in file_segs_deleted_num.keys():
        print("key: " + str(key) + "   file_segs_deleted_num:  " + file_segs_deleted_num[key].__str__())


def test_segs_updated_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    file_segs_updated_num = get_segs_updated_num(file_dict)
    for key in file_segs_updated_num.keys():
        print("key: " + str(key) + "    file_segs_updated_num:  " + file_segs_updated_num[key].__str__())


def test_test_inclusion():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    file_test_inclusion = get_test_inclusion(file_dict)
    for key in file_test_inclusion.keys():
        print("key: " + str(key) + "    file_test_inclusion:  " + file_test_inclusion[key].__str__())


def test_subsystem_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    file_subsystem_num = get_subsystem_num(file_dict)
    for key in file_subsystem_num.keys():
        print("key: " + str(key) + "    file_subsystem_num:  " + file_subsystem_num[key].__str__())




def test_changes_files_modified_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_file_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]][data[index][2]] = {data[index][9]}
        index = index + 1
    changes_files_modified_num = get_changes_files_modified_num(file_dict)
    for key in changes_files_modified_num.keys():
        print("key: " + str(key) + "    changes_files_modified_num:  " + changes_files_modified_num[key].__str__())


def test_file_developer_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]]= data[index][25]
        index = index + 1
    file_developer_num = get_file_developer_num(file_dict)
    for key in file_developer_num.keys():
        print("key: " + str(key) + "    file_developer_num:  " + file_developer_num[key].__str__())


def test_file_developer_change_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]]= data[index][25]
        index = index + 1
    file_developer_change_num = get_file_developer_change_num(file_dict)
    for key in file_developer_change_num.keys():
        print("key: " + str(key) + "    file_developer_change_num:  " + file_developer_change_num[key].__str__())


def test_file_developer_recent_change_num():
    global pushed_time, time_dict, index
    # 利用游标对象进行操作
    cursor.execute(pr_sql)
    data = cursor.fetchall()
    print(data.__len__())
    file_dict = {}
    index = 0
    while index < data.__len__():
        if file_dict.__contains__(data[index][0]) is False:
            file_dict[data[index][0]] = {}
        file_dict[data[index][0]]= {}
        file_dict[data[index][0]]['commit_content']=data[index][25]
        file_dict[data[index][0]]['created_at'] = data[index][10]
        index = index + 1
    file_developer_recent_change_num= get_file_developer_recent_change_num(file_dict)
    for key in file_developer_recent_change_num.keys():
        print("key: " + str(key) + "    file_developer_recent_change_num:  " + file_developer_recent_change_num[key].__str__())


# 数据操作部分
# SQL语句书写
# repo_sql = """select * from pr_repo"""
pr_sql = """select * from pr_self"""
pr_file_sql = """select pr_number,repo_name,changed_file_name,sha,changed_file_status,lines_added_num,lines_deleted_num,lines_changed_num,contain_patch,patch_content from pr_file"""
# 链接数据库
database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
# 创建游标对象
cursor = database.cursor()
test_file_developer_recent_change_num()
# 关闭数据库连接
database.close()

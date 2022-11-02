'''
获取到所有的PR信息，找出每一个PR创建的时间，以及在该PR创建时间那个时刻仍处于open状态的pr，
然后将这个时刻还处于open状态的pr作为输入X。
FIFO算法，根据pr创建的时间先创建，放在最前面，这样对上述pr列表进行排序。FIFOY
真实排序：在该时刻之后，该X中，被相应，或者被关闭或者被合并等发生改变的时间，根据该时间顺序进行排序，进而获取真实排序TRUEY
将FIFOY，与TRUEY进行比较，通过NDGC进行比较，判断排序效果
'''
import json

import pymysql
from utils.path_exist import path_exists_or_create

import csv
import os

# 增加代码的可读性
pr_number_index = 0
pr_user_id_index = 1
pr_author_association_index = 2
comments_number_index = 3
comments_content_index = 4
review_comments_number_index = 5
review_comments_content_index = 6
pr_user_name_index = 7

header = ["PR创建者", "PR创建者的身份",  "评论过的用户数量（含PR创建者自身）","评论过该PR创建者的用户（含PR创建者自身）", "评论过的用户数量（不含PR创建者自身）","评论过该PR创建者的用户（不含PR创建者自身）"]


def getDataFromSql(sqlOrder):
    ##连接数据库
    conn = pymysql.connect(
        host="127.0.0.1",  # "172.19.241.129",
        port=3306,  # 端口号
        user="root",  # 数据库用户
        password="root",  # 数据库密码
        database="pr_second"  # 要连接的数据库名称
    )

    cursor = conn.cursor()  # 游标

    ###从username数据库获取所有的name
    sql = sqlOrder
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    return data


def get_comment_people_name(comment):
    comment_dict = json.loads(comment)
    re_data = set()
    if len(comment_dict) == 0:
        return re_data
    else:
        for comment_temp in comment_dict:
            re_data.add(comment_temp["user"]["login"])
        return re_data


def get_data_by_repo_name(repo_name):
    # 从数据库获取数据
    raw_data = getDataFromSql(
        "select * from pr_self where repo_name='" + repo_name + "' and closed_at is not null order by pr_number")

    print(len(raw_data))  ##查看PR数量

    # 标记有用的PR自身信息的下标
    useful_features_index = [0,  ##pr_number
                             3,  ##pr_user_id
                             5,  ##pr_author_association
                             20,  ##comments_number
                             21,  ##comments_content
                             22,  ##review_comments_number
                             23,  ##review_comments_content
                             4,  ##pr_user_name
                             ]

    selected_data = []  ##保留有用的属性特征
    for item in raw_data:
        tmp = []
        for i in useful_features_index:
            tmp.append(item[i])
        selected_data.append(tmp)
    re_dict = dict()
    for item in selected_data:
        temp_set = set()
        if item[comments_number_index] != 0:
            comments_people = get_comment_people_name(item[comments_content_index])
            if len(comments_people) != 0:
                for temp_people in comments_people:
                    temp_set.add(temp_people)
        if item[review_comments_number_index] != 0:
            review_people = get_comment_people_name(item[review_comments_content_index])
            if len(review_people) != 0:
                for temp_people in review_people:
                    temp_set.add(temp_people)
        if re_dict.get(item[pr_user_name_index]) == None:
            re_dict[item[pr_user_name_index]]=dict()
            re_dict[item[pr_user_name_index]]["people"] = temp_set
            re_dict[item[pr_user_name_index]]["pr_author_association"] = item[pr_author_association_index]
        elif len(temp_set) != 0:
            for temp_people in temp_set:
                re_dict[item[pr_user_name_index]]["people"].add(temp_people)
    write_data = []
    for key in re_dict.keys():
        tmp = []
        tmp.append(key)
        tmp.append(re_dict[key]["pr_author_association"])
        tmp.append(len(re_dict[key]["people"]))
        if len(re_dict[key]["people"])==0:
            tmp.append("")
        else:
            tmp.append(str(re_dict[key]["people"]))
        # 删除自身
        if re_dict[key]["people"].__contains__(key):
            re_dict[key]["people"].remove(key)
        tmp.append(len(re_dict[key]["people"]))
        if len(re_dict[key]["people"]) == 0:
            tmp.append("")
        else:
            tmp.append(str(re_dict[key]["people"]))

        write_data.append(tmp)

    with open(test_filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)
        # write the data
        writer.writerows(write_data)
    return re_dict


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name = "guacamole-client"
    file_path = "./people/" + repo_name + "/"
    path_exists_or_create(file_path)

    test_filename = file_path + repo_name + "_pr_people_data.csv"
    row_data = get_data_by_repo_name(repo_name)
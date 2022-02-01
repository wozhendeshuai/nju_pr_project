import time

import pymysql

import java_project.data_processing_engineering.project_database_connection as dbConnection
from baseline.true_order import get_true_order_dict
from evaluation_index.Kendall_tau_distance import kendall_tau_distance
from evaluation_index.mrr import mrr
from utils.date_utils.date_function import get_waiting_time, get_close_pr_time
import csv
from evaluation_index.ndcg import ndcg
# Python的标准库linecache模块非常适合这个任务
import linecache
import os
import xgboost as xgb
from xgboost import DMatrix
from sklearn.datasets import load_svmlight_file

# 增加代码的可读性
from utils.path_exist import path_exists_or_create

pr_number_index = 0
repo_name_index = 1
pr_user_id_index = 2
pr_user_name_index = 3
pr_author_association_index = 4
labels_index = 5
created_at_index = 6
closed_at_index = 7
merged_at_index = 8
updated_at_index = 9
merged_index = 10
mergeable_state_index = 11
assignees_content_index = 12
comments_number_index = 13
comments_content_index = 14
review_comments_number_index = 15
review_comments_content_index = 16
commit_number_index = 17
changed_file_num_index = 18
total_add_line_index = 19
total_delete_line_index = 20
title_index = 21
body_index = 22


def save_data(group_data, output_feature, output_group):
    '''
    保存xgboost相关数据，将原始数据转换成xgboost需要的数据，输出到文件
    '''
    if len(group_data) == 0:
        return

    output_group.write(str(len(group_data)) + "\n")
    for data in group_data:
        # only include nonzero features
        feats = [p for p in data[2:] if float(p.split(':')[1]) != 0.0]
        output_feature.write(data[0] + " " + " ".join(feats) + "\n")


def prepare_xgboostData(original_data_path, output_feature_path, output_group_path):
    '''
    保存xgboost相关数据，将原始数据转换成xgboost需要的数据
    '''
    fi = open(original_data_path)
    output_feature = open(output_feature_path, "w")
    output_group = open(output_group_path, "w")
    group_data = []
    group = ""
    for line in fi:
        if not line:
            break
        if "#" in line:
            line = line[:line.index("#")]
        splits = line.strip().split(" ")
        if splits[1] != group:
            save_data(group_data, output_feature, output_group)
            group_data = []
        group = splits[1]
        group_data.append(splits)
    save_data(group_data, output_feature, output_group)
    fi.close()
    output_feature.close()
    output_group.close()


# 根据所在原始文件中pr_number获取当前测试需要的文件
# 获取当前文件中pr——number，以及对应的索引位置
def get_pr_number_from_origin_data_path(origin_data_path):
    file_pr_dict = {}
    open_pr_list = []
    count = 0
    for line in open(origin_data_path):
        line_str = line.partition("# ")
        file_pr_dict[int(line_str[2])] = count
        count = count + 1
        open_pr_list.append(int(line_str[2]))
    return open_pr_list, file_pr_dict


# 根据已有数据得到排序结果
def model_result(open_data_path,
                 xgboost_temp_open_data_path,
                 xgboost_temp_open_group_data_path):
    # 使用模型
    tar = xgb.Booster(model_file=model_path)
    open_pr_list, file_pr_dict = get_pr_number_from_origin_data_path(open_data_path)
    print(open_pr_list, file_pr_dict)
    print("模型计算中：")
    # 将该文件再转换未xgboost支持的文件进行计算
    prepare_xgboostData(open_data_path, xgboost_temp_open_data_path, xgboost_temp_open_group_data_path)
    x_test, y_test = load_svmlight_file(xgboost_temp_open_data_path)
    test_dmatrix = DMatrix(x_test)
    # 使用模型预测结果
    pre = tar.predict(test_dmatrix)
    print(pre)
    pre_result = {}
    for i in range(open_pr_list.__len__()):
        pre_result[open_pr_list[i]] = pre[i]
    pre_list = pre.tolist()
    pre_list.sort(reverse=True)

    sort_result = []
    sort_result_dict = {}
    for index in range(pre_list.__len__()):
        score = pre_list[index]
        for key in pre_result.keys():
            if pre_result.get(key) == score and (sort_result.__len__() == 0 or sort_result.__contains__(key) is False):
                sort_result.append(key)
                sort_result_dict[key] = score
                break
    print(sort_result)
    print(sort_result_dict)
    return sort_result


# Press the green button in the gutter to run the script.
def save_result_to_sql(data_time, repo_name, alg_name, sort_result):
    # 从数据库获取数据
    select_sql = "select * from alg_sort_result where repo_name='" + repo_name + "' and  sort_day='" + data_time + "' and alg_name='" + alg_name + "'"
    print(select_sql)
    raw_data = dbConnection.getDataFromSql(select_sql, "project_sort_db")
    ##连接数据库
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,  # 端口号
        user="root",  # 数据库用户
        password="root",  # 数据库密码
        database="project_sort_db"  # 要连接的数据库名称
    )
    cursor = conn.cursor()  # 游标
    # 若今天还未插入数据则，走插入逻辑
    if raw_data.__len__() == 0:
        for pr_number_index in range(sort_result.__len__()):
            insert_sqlData = (
                data_time,
                repo_name,
                alg_name,
                sort_result[pr_number_index], pr_number_index)
            insert_result_to_db(conn, cursor, insert_sqlData)
    # 若今天已插入数据，则更新相关内容
    elif raw_data.__len__() > 0:
        # 先把真实长度的数据进行更新和新增
        true_len = sort_result.__len__()
        raw_data_pr_number_dict = {}
        delete_pr_numbers=[]
        for temp_index in range(raw_data.__len__()):
            raw_data_pr_number_dict[raw_data[temp_index][3]] = temp_index
            #判断是否有不在最新结果集的pr_number
            flag=False
            for i in range(sort_result.__len__()):
                if raw_data[temp_index][3] == sort_result[i]:
                    flag=True
                    break
            if flag is False:
                delete_pr_numbers.append(raw_data[temp_index][3])
        for temp_index in range(true_len):
            # 如果raw_data存在，则更新，否则就插入，如果结束之后，还是已存在的多，则删除多余的已存在的，如果是新的多，则已被插入
            pr_number_temp = sort_result[temp_index]
            if raw_data_pr_number_dict.__contains__(pr_number_temp):
                #补齐更新语句
                update_sql_data = (temp_index, data_time,repo_name,alg_name,sort_result[temp_index])
                update_result_to_db( conn, cursor, update_sql_data)
            else:
                # 不在已有的结果集中可以插入
                insert_sql_data = (data_time,repo_name,alg_name,sort_result[temp_index], temp_index)
                insert_result_to_db( conn, cursor, insert_sql_data)

        for temp_index in range(delete_pr_numbers.__len__()):
            pr_number_temp = delete_pr_numbers[temp_index]
            delete_sql_data = (data_time, repo_name, alg_name, pr_number_temp)
            delete_result_to_db(conn,cursor,delete_sql_data)


# 更新语句
def update_result_to_db( conn, cursor, sqlData):
    updata_sql = """
        update   alg_sort_result set
        pr_order = %s
        where sort_day=%s and repo_name=%s and alg_name=%s and pr_number=%s"""

    # 执行sql语句
    cursor.execute(updata_sql, sqlData)
    # 提交到数据库执行
    conn.commit()
    print(sqlData, "数据更新成功")


# 删除语句
def delete_result_to_db( conn, cursor, sqlData):
    updata_sql = """
        delete  from alg_sort_result 
        where sort_day=%s and repo_name=%s and alg_name=%s and pr_number=%s"""

    # 执行sql语句
    cursor.execute(updata_sql, sqlData)
    # 提交到数据库执行
    conn.commit()
    print(sqlData, "数据删除成功")
# 插入语句
def insert_result_to_db( conn, cursor, sqlData):
    insert_sql = """
        insert into alg_sort_result(
        sort_day,
        repo_name, 
        alg_name,
        pr_number,
        pr_order)
        VALUES( %s,%s,%s, %s,%s )
       """
    # 执行sql语句
    cursor.execute(insert_sql, sqlData)
    # 提交到数据库执行
    conn.commit()
    print(sqlData, "数据插入成功")


if __name__ == '__main__':
    repo_name = "helix"

    # xgboost所能调的库
    alg_name = "xgboost"
    rank_style = "pairwise"
    data_time = time.strftime("%Y-%m-%d", time.localtime())
    # 测试模型性能的文件路径
    open_file_path = "../data_processing_engineering/rank_data/open/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(open_file_path)
    open_data_path = open_file_path + repo_name + "_open_svm_rank_format_data_" + data_time + ".txt"
    xgboost_open_file_path = "../data_processing_engineering/xgboost_data/open/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_open_file_path)
    xgboost_temp_open_data_path = xgboost_open_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_" + data_time + ".txt"
    xgboost_temp_open_group_data_path = xgboost_open_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_group_" + data_time + ".txt"

    xgboost_model_path = "./rank_model/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_model_path)
    model_path = xgboost_model_path + repo_name + "_" + alg_name + "_" + rank_style + "_model_" + data_time + ".txt"

    # xgboost_result_path = "./result/xgboost/" + repo_name + "/open/" + data_time + "/"
    # path_exists_or_create(xgboost_result_path)
    # result_path = xgboost_result_path + repo_name + "_" + alg_name + "_result_" + data_time + ".csv"

    # 首先运行算法训练模型
    sort_result = model_result(open_data_path, xgboost_temp_open_data_path, xgboost_temp_open_group_data_path)
    save_result_to_sql(data_time, repo_name, alg_name + ":" + rank_style, sort_result)

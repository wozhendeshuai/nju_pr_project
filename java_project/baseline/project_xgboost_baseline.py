import sys
import time

import pymysql
import os
import csv
import xgboost as xgb
from xgboost import DMatrix
from sklearn.datasets import load_svmlight_file

# 增加代码的可读性
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
    count = 0
    for line in open(origin_data_path):
        line_str = line.partition("# ")
        file_pr_dict[int(line_str[2])] = count
        count = count + 1
    return file_pr_dict


def get_data_by_repo_name_and_origin_data_path(origin_data_path, repo_name):
    data = dbConnection.getDataFromSql(
        "select * from pr_self where repo_name='" + repo_name + "' and closed_at is not null order by pr_number")

    print(len(data))  ##查看PR数量
    # 获取所在文件中的prlist
    file_pr_dict = get_pr_number_from_origin_data_path(origin_data_path)
    # 标记有用的PR自身信息的下标
    useful_features_index = [0,  ##pr_number
                             2,  ##repo_name
                             3,  ##pr_user_id
                             4,  ##pr_user_name
                             5,  ##pr_author_association
                             8,  ##labels
                             10,  ##created_at
                             12,  ##closed_at
                             13,  ##merged_at
                             11,  ##updated_at
                             14,  ##merged
                             16,  ##mergeable_state
                             18,  ##assignees_content
                             20,  ##comments_number
                             21,  ##comments_content
                             22,  ##review_comments_number
                             23,  ##review_comments_content
                             24,  ##commit_number
                             26,  ##changed_file_num
                             27,  ##total_add_line
                             28,  ##total_delete_line
                             6,  ##title
                             7,  ##body
                             ]

    ##保留有用的属性特征
    selected_data = []
    for item in data:
        tmp = []
        for i in useful_features_index:
            tmp.append(item[i])
        selected_data.append(tmp)
    # 获取每个PR的响应时间
    first_response_time = []
    # 记录pr_number在大文件中的顺序
    pr_number_index_list = []
    day_data = {}
    for item in selected_data:
        tmp = []
        created_time = item[created_at_index]
        created_day = created_time.date()
        if day_data.__contains__(created_day):
            day_data[created_day][item[pr_number_index]] = {}
            day_data[created_day][item[pr_number_index]]['created_time'] = item[created_at_index]
            day_data[created_day][item[pr_number_index]]['closed_time'] = item[closed_at_index]
        else:
            day_data[created_day] = {}
            day_data[created_day][item[pr_number_index]] = {}
            day_data[created_day][item[pr_number_index]]['created_time'] = item[created_at_index]
            day_data[created_day][item[pr_number_index]]['closed_time'] = item[closed_at_index]
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('updated_time', item[updated_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp.append(('comments_number', item[comments_number_index]))
        tmp.append(('comments_content', item[comments_content_index]))
        tmp.append(('review_comments_number', item[review_comments_number_index]))
        tmp.append(('review_comments_content', item[review_comments_content_index]))
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp = dict(tmp)
        first_response_time.append((item[pr_number_index], tmp))
        pr_number_index_list.append(item[pr_number_index])
    pr_number_index_list.sort()
    pr_number_index_dict = {}
    count = 0
    for item in pr_number_index_list:
        pr_number_index_dict[item] = count
        count = count + 1
    first_response_time_dict = dict(first_response_time)
    first_response_time_dict = get_close_pr_time(first_response_time_dict)  # get_waiting_time(first_response_time_dict)
    # print(first_response_time_dict)
    # 响应时间 按照pr_number的顺序进行排列
    response_time = []
    for item in first_response_time_dict.keys():
        response_time.append(first_response_time_dict[item])
    return day_data, response_time, first_response_time_dict, file_pr_dict


def prepare_temp_file(temp_data_path, origin_data_path, open_pr_index_list, day):
    file = open(temp_data_path, 'w+')
    for i in range(len(open_pr_index_list)):
        s = getline(origin_data_path, open_pr_index_list[i] + 1)
        file.write(s)
    file.close()
    print("保存第 " + str(day) + " 天的临时文件成功")


# 可显示使用循环, 注意enumerate从0开始计数，而line_number从1开始
def getline(the_file_path, line_number):
    if line_number < 1:
        return ''
    for cur_line_number, line in enumerate(open(the_file_path, 'rU')):
        if cur_line_number == line_number - 1:
            return line
    return ''


# 根据已有数据得到排序结果
def model_result(day_data, day, pr_number_index_dict, origin_data_path, temp_data_path, temp_sort_result_path,
                 model_path, xgboost_temp_data_path, xgboost_temp_group_data_path):
    # 使用模型
    tar = xgb.Booster(model_file=model_path)

    open_pr_list = []
    open_pr_index_list = []
    sort_result = []
    # 得到本日以及本日之前还处于开放状态的pr_number，并利用已训练好的模型，重新排序，并把排序的结果读取出来
    for key in day_data.keys():
        if key > day:
            continue
        else:
            # 获取当前天的所有openPR
            temp_pr_dict = day_data[key]
            for pr_key in temp_pr_dict:
                if pr_number_index_dict.__contains__(pr_key) is False or temp_pr_dict[pr_key][
                    'closed_time'].date() < day:
                    continue
                else:
                    open_pr_list.append(pr_key)
                    open_pr_index_list.append(pr_number_index_dict.get(pr_key))
    if open_pr_list.__len__() == 0:
        return sort_result
    print("模型计算中：")
    prepare_temp_file(temp_data_path, origin_data_path, open_pr_index_list, day)
    # 将该文件再转换未xgboost支持的文件进行计算
    prepare_xgboostData(temp_data_path, xgboost_temp_data_path, xgboost_temp_group_data_path)
    x_test, y_test = load_svmlight_file(xgboost_temp_data_path)
    test_dmatrix = DMatrix(x_test)
    # 使用模型预测结果
    pre = tar.predict(test_dmatrix)
    pre_result = {}
    for i in range(open_pr_list.__len__()):
        pre_result[open_pr_list[i]] = pre[i]
    pre_list = pre.tolist()
    pre_list.sort(reverse=True)
    for index in range(pre_list.__len__()):
        score = pre_list[index]
        for key in pre_result.keys():
            if pre_result.get(key) == score and (sort_result.__len__() == 0 or sort_result.__contains__(key) is False):
                sort_result.append(key)
                break
    return sort_result


# 根据所在打开状态文件中pr_number获取当前测试需要的文件
# 获取当前打开状态文件中pr——number，以及对应的索引位置
def get_open_pr_number_from_origin_data_path(origin_data_path):
    file_pr_dict = {}
    open_pr_list = []
    count = 0
    for line in open(origin_data_path):
        line_str = line.partition("# ")
        file_pr_dict[int(line_str[2])] = count
        count = count + 1
        open_pr_list.append(int(line_str[2]))
    return open_pr_list, file_pr_dict


# 根据打开状态的据得到排序结果
def open_model_result(open_data_path,
                      xgboost_temp_open_data_path,
                      xgboost_temp_open_group_data_path):
    print("================================计算打开状态PR的优先级排序列表==" + open_data_path + "==========")
    # 使用模型
    tar = xgb.Booster(model_file=model_path)
    open_pr_list, file_pr_dict = get_open_pr_number_from_origin_data_path(open_data_path)
    print(open_pr_list, file_pr_dict)
    print("模型计算中：")
    # 将该文件再转换未xgboost支持的文件进行计算
    prepare_xgboostData(open_data_path, xgboost_temp_open_data_path, xgboost_temp_open_group_data_path)
    x_test, y_test = load_svmlight_file(xgboost_temp_open_data_path)
    test_dmatrix = DMatrix(x_test)
    # 使用模型预测结果
    pre = tar.predict(test_dmatrix)
    print("模型计算结果：")
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
    print("结束==========================结束计算打开状态PR的优先级排序列表==" + open_data_path + "=结束=========")
    return sort_result


# 对模型进行调用，同时将数据写入到文件中，方便后续统计
def alg_model_result(true_rate_label_dict, day_data, pr_number_index_dict, origin_data_path, temp_data_path,
                     temp_sort_result_path, model_path, xgboost_temp_data_path, xgboost_temp_group_data_path,
                     result_path, data_time, repo_name, alg_name):
    ndcg_list = []
    day_list = []
    mrr_list = []
    kendall_list = []
    max_day = None
    min_day = None
    for day in day_data.keys():
        print("=================================日期:", day)
        # 获取每一天还处于open状态的pr列表顺序
        sort_result = model_result(day_data, day, pr_number_index_dict, origin_data_path, temp_data_path,
                                   temp_sort_result_path, model_path, xgboost_temp_data_path,
                                   xgboost_temp_group_data_path)
        if sort_result.__len__() == 0:
            print("在" + origin_data_path + "无相关pr")
            continue
        rank_sort = []
        true_sort = []
        # 获取从fifo中获取的每个列表的顺序
        for pr_number_result in sort_result:
            rank_sort.append(true_rate_label_dict[pr_number_result])
            true_sort.append(true_rate_label_dict[pr_number_result])
        true_sort.sort(reverse=True)
        ndcg_num = ndcg(true_sort, rank_sort, rank_sort.__len__())
        mrr_num = mrr(true_sort, rank_sort)
        kendall_num = kendall_tau_distance(true_sort, rank_sort)
        print("pr_number排序:", sort_result)
        print("rank_sort:", rank_sort)
        print("true_sort:", true_sort)
        print("ndcg_num:", ndcg_num)
        print("mrr_num:", mrr_num)
        print("kendall_num:", kendall_num)
        if max_day is None or max_day < day:
            max_day = day
        if min_day is None or min_day > day:
            min_day = day
        day_list.append(day)
        ndcg_list.append(ndcg_num)
        mrr_list.append(mrr_num)
        kendall_list.append(kendall_num)

    headers = ['日期',
               'ndcg',
               'mrr',
               'kendall_tau_distance'
               ]
    row_data = []
    for i in range(len(day_list)):
        tmp = []
        tmp.append(day_list[i])
        tmp.append(ndcg_list[i])
        tmp.append(mrr_list[i])
        tmp.append(kendall_list[i])
        row_data.append(tmp)
        save_test_result_to_sql(data_time, repo_name, alg_name, day_list[i], ndcg_list[i], mrr_list[i], kendall_list[i])

    print(row_data)
    # 保存数据到csv文件
    with open(result_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in row_data:
            writer.writerow(item)
    return None


# 训练模型
def train_model(alg_name, rank_type, model_path, train_data_path, train_data_group_path, test_data_path):
    print("===============训练模型+" + alg_name + "======================")

    #  This script demonstrate how to do ranking with xgboost.train
    x_train, y_train = load_svmlight_file(train_data_path)
    x_test, y_test = load_svmlight_file(test_data_path)

    group_train = []
    with open(train_data_group_path, "r") as f:
        data = f.readlines()
        for line in data:
            group_train.append(int(line.split("\n")[0]))

    train_dmatrix = DMatrix(x_train, y_train)

    test_dmatrix = DMatrix(x_test)

    train_dmatrix.set_group(group_train)

    params = {'objective': 'rank:' + rank_type, 'eta': 0.1, 'gamma': 1.0,
              'min_child_weight': 0.1, 'max_depth': 6}
    xgb_model = xgb.train(params, train_dmatrix, num_boost_round=4,
                          evals=[(train_dmatrix, 'validation')])
    xgb_model.save_model(model_path)
    # 使用模型
    tar = xgb.Booster(model_file=model_path)
    pre = tar.predict(test_dmatrix)
    for temp in pre:
        print(temp)
    print("===============结束训练模型+" + alg_name + "======================")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    path_temp = os.path.dirname(sys.path[0])
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 当前的环境为： ", path_temp)
    sys.path.append(path_temp)
    path_temp = os.path.dirname(path_temp)
    sys.path.append(path_temp)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 当前的环境为： " + path_temp)

    import java_project.data_processing_engineering.project_database_connection as dbConnection
    from baseline.true_order import get_true_order_dict
    from evaluation_index.Kendall_tau_distance import kendall_tau_distance
    from evaluation_index.mrr import mrr
    from java_project.baseline.save_to_project_sql import save_test_result_to_sql, save_result_to_sql
    from utils.date_utils.date_function import get_close_pr_time
    from evaluation_index.ndcg import ndcg
    from utils.path_exist import path_exists_or_create

    repo_name = sys.argv[1]  # "tajo"
    # ranklib所能调的库
    alg_name = "xgboost"
    rank_style = "pairwise"
    data_time = time.strftime("%Y-%m-%d", time.localtime())

    # 测试模型性能的文件路径
    file_path = "../data_processing_engineering/rank_data/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(file_path)
    origin_data_path = file_path + repo_name + "_svm_rank_format_test_data_" + data_time + ".txt"
    temp_data_path = file_path + repo_name + "_temp_svm_rank_format_data_" + data_time + ".txt"
    # 训练模型的文件路径
    train_data_path = file_path + repo_name + "_svm_rank_format_train_data_" + data_time + ".txt"
    test_data_path = file_path + repo_name + "_svm_rank_format_test_data_" + data_time + ".txt"

    xgboost_file_path = "../data_processing_engineering/xgboost_data/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_file_path)
    xgboost_temp_data_path = xgboost_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_" + data_time + ".txt"
    xgboost_temp_group_data_path = xgboost_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_group_" + data_time + ".txt"
    temp_sort_result_path = xgboost_file_path + repo_name + "_" + rank_style + "_myScoreFile_" + data_time + ".txt"
    xgboost_train_data_path = xgboost_file_path + repo_name + "_xgboost_svm_rank_format_train_data_" + data_time + ".txt"
    xgboost_train_data_group_path = xgboost_file_path + repo_name + "_xgboost_svm_rank_format_train_group_data_" + data_time + ".txt"
    xgboost_test_data_path = xgboost_file_path + repo_name + "_xgboost_svm_rank_format_test_data_" + data_time + ".txt"
    xgboost_test_data_group_path = xgboost_file_path + repo_name + "_xgboost_svm_rank_format_test_group_data_" + data_time + ".txt"

    xgboost_model_path = "./rank_model/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_model_path)
    model_path = xgboost_model_path + repo_name + "_" + alg_name + "_" + rank_style + "_model_" + data_time + ".txt"

    xgboost_result_path = "./result/xgboost/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_result_path)
    result_path = xgboost_result_path + repo_name + "_" + alg_name + "_result_" + data_time + ".csv"

    prepare_xgboostData(train_data_path, xgboost_train_data_path, xgboost_train_data_group_path)
    prepare_xgboostData(test_data_path, xgboost_test_data_path, xgboost_test_data_group_path)

    # 首先运行算法训练模型
    train_model(alg_name, rank_style, model_path, xgboost_train_data_path, xgboost_train_data_group_path,
                xgboost_test_data_path)
    print(alg_name + "模型训练完成==========")
    day_data, response_time, first_response_time_dict, pr_number_index_dict = get_data_by_repo_name_and_origin_data_path(
        origin_data_path, repo_name)
    true_rate_label_dict = get_true_order_dict(response_time, first_response_time_dict)
    alg_model_result(true_rate_label_dict, day_data, pr_number_index_dict, origin_data_path, temp_data_path,
                     temp_sort_result_path, model_path, xgboost_temp_data_path, xgboost_temp_group_data_path,
                     result_path, data_time, repo_name, alg_name + ":" + rank_style)

    # 打开PR的文件路径
    open_file_path = "../data_processing_engineering/rank_data/open/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(open_file_path)
    open_data_path = open_file_path + repo_name + "_open_svm_rank_format_data_" + data_time + ".txt"
    xgboost_open_file_path = "../data_processing_engineering/xgboost_data/open/" + repo_name + "/" + data_time + "/"
    path_exists_or_create(xgboost_open_file_path)
    xgboost_temp_open_data_path = xgboost_open_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_" + data_time + ".txt"
    xgboost_temp_open_group_data_path = xgboost_open_file_path + repo_name + "_xgboost_temp_svm_rank_format_data_group_" + data_time + ".txt"
    # 首先运行算法训练模型
    sort_result = open_model_result(open_data_path, xgboost_temp_open_data_path, xgboost_temp_open_group_data_path)
    save_result_to_sql(data_time, repo_name, alg_name + ":" + rank_style, sort_result)

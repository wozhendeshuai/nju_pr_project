'''
获取到所有的PR信息，找出每一个PR创建的时间，以及在该PR创建时间那个时刻仍处于open状态的pr，
然后将这个时刻还处于open状态的pr作为输入X。
FIFO算法，根据pr创建的时间先创建，放在最前面，这样对上述pr列表进行排序。FIFOY
真实排序：在该时刻之后，该X中，被相应，或者被关闭或者被合并等发生改变的时间，根据该时间顺序进行排序，进而获取真实排序TRUEY
将FIFOY，与TRUEY进行比较，通过ndcg进行比较，判断排序效果
'''
import data_processing_engineering.get_data_from_database.database_connection as dbConnection
from baseline.true_order import get_true_order_dict
from evaluation_index.Kendall_tau_distance import kendall_tau_distance
from evaluation_index.mrr import mrr
from utils.date_utils.date_function import get_waiting_time, get_close_pr_time
import csv
from evaluation_index.ndcg import ndcg
# Python的标准库linecache模块非常适合这个任务
import linecache
import os
import pandas as pd
import xgboost as xgb
from xgboost import DMatrix
from sklearn.datasets import load_svmlight_file
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import seaborn as sns
from utils.path_exist import path_exists_or_create
from utils.print_photo import showBN
from pgmpy.models import BayesianNetwork, BayesianModel
from pgmpy.estimators import BayesianEstimator
# 用结构学习建立模型
# %%
from pgmpy.estimators import HillClimbSearch
from pgmpy.estimators import K2Score, BicScore

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
# 获取当前文件中pr——number，以及对应的索引位置 读取csv文件
def get_pr_number_from_origin_data_path(origin_data_path):
    test = pd.read_csv(origin_data_path)
    file_pr_dict = {}
    pr_number_series = test.get("pr_number")
    for i in range(pr_number_series.__len__()):
        print(str(i) + "   pr_number_series   " + str(pr_number_series[i]))
        file_pr_dict[pr_number_series[i]] = i
    return file_pr_dict


# 得到在文件中的pr相关信息
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
def model_result(day_data, day, pr_number_index_dict, result_rate_in_dict):
    # 使用模型
    open_pr_list = []
    # 记录每日打开的PR-number以及其被模型计算的结果
    open_pr_index_dict = {}
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
                    open_pr_index_dict[pr_key] = result_rate_in_dict.get(pr_key)
    if open_pr_list.__len__() == 0:
        return sort_result
    temp_sort_tmp = []
    print("文件结果获取计算中======")
    for index in range(open_pr_list.__len__()):
        pr_number = open_pr_list[index]
        if result_rate_in_dict.__contains__(pr_number):
            # 先记录每个PR被模型算出来的序列
            temp_sort_tmp.append(result_rate_in_dict.get(pr_number))
    temp_sort_tmp.sort(reverse=True)
    temp_pr_number_sort_tmp = []
    for index in range(temp_sort_tmp.__len__()):
        for temp_key in open_pr_index_dict.keys():
            if open_pr_index_dict.get(temp_key) == temp_sort_tmp[index] and temp_pr_number_sort_tmp.__contains__(
                    temp_key) is False:
                temp_pr_number_sort_tmp.append(temp_key)
    return temp_pr_number_sort_tmp


# 对模型进行调用，同时将数据写入到文件中，方便后续统计
def alg_model_result(true_rate_label_dict, day_data, pr_number_index_dict, result_rate_in_dict, result_path):
    ndcg_list = []
    day_list = []
    mrr_list = []
    kendall_list = []
    max_day = None
    min_day = None
    for day in day_data.keys():
        print("=================================日期:", day)
        # 获取每一天还处于open状态的pr列表顺序
        sort_result = model_result(day_data, day, pr_number_index_dict, result_rate_in_dict)
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
        ndcg_num = ndcg(true_sort, rank_sort, rank_sort.__len__(),form = "exp")
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
    print(row_data)
    # 保存数据到csv文件
    with open(result_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in row_data:
            writer.writerow(item)
    return None


# 训练模型并得到在测试集上的结果
def train_model_and_result(alg_name, train_data_path, test_data_path, repo_name):
    module_result = {}
    print("===============训练模型+" + alg_name + "======================")

    train = pd.read_csv(train_data_path)
    train_dataset = train.drop(columns=['pr_number'])
    train_dataset.dropna(inplace=True)
    train_dataset['priorities_number'] = train_dataset['priorities_number'].astype(int)
    print(train_dataset.head())
    bayesian_model_path = "./rank_model/bayesian_network/" + repo_name + "/"
    directory = bayesian_model_path + "photo/"
    path_exists_or_create(directory)

    hc = HillClimbSearch(train_dataset)  # HillClimbSearch(train, scoring_method=BicScore(train))
    best_model = hc.estimate(scoring_method="k2score", max_indegree=4, max_iter=int(1e4))
    print(best_model.edges())
    showBN(best_model, True, repo_name + "_BayesianModel.gv", directory)
    best_model = BayesianModel(best_model.edges())
    best_model.fit(train_dataset, estimator=BayesianEstimator, prior_type="BDeu")  # default equivalent_sample_size=5
    for key in best_model.nodes:
        print(key)
    model_directory = bayesian_model_path + "model/"
    path_exists_or_create(model_directory)
    best_model.save(filename=model_directory + repo_name + "_BayesianModel.bif",filetype="bif")
    # best_model=BayesianNetwork.load(filename=repo_name+"_BayesianModel.bif", filetype="bif")
    print("===============结束训练模型+" + alg_name + "======================")

    print("===============开始利用模型计算结果+" + alg_name + "======================")
    test = pd.read_csv(test_data_path)
    test_dataset = test.drop(columns=['pr_number'])
    test_dataset.dropna(inplace=True)
    test_dataset['priorities_number'] = test_dataset['priorities_number'].astype(int)
    predict_data = test_dataset.drop(columns='priorities_number', axis=1)
    print(set(predict_data.columns) - set(best_model.nodes()))

    temp_data = predict_data
    temp_set = set(predict_data.columns) - set(best_model.nodes())
    # 去除不在模型中的节点
    for key in temp_set:
        temp_data = temp_data.drop(columns=key, axis=1)
    y_pred = None
    for row_index in range(temp_data.__len__()):
        try:
            y_pred_temp = best_model.predict(temp_data.loc[[row_index]], n_jobs=1)
        except Exception as e:
            # 如果发生错误则回滚
            print("第", row_index, "行数据预测失败原因是: ", e)
            y_pred_temp = pd.DataFrame({"priorities_number": [0]})
        if y_pred is None:
            y_pred = y_pred_temp
        else:
            y_pred = y_pred.append(y_pred_temp, ignore_index=True)

    # y_pred = best_model.predict(temp_data, n_jobs=1)

    print(y_pred)
    result_directory = bayesian_model_path + "result/"
    path_exists_or_create(result_directory)
    y_pred.to_csv(result_directory + repo_name + "_bayesian_network_result.csv", index=0)
    test_pr_number = pd.read_csv(test_data_path)
    pr_number_series = test_pr_number.get("pr_number")
    y_pred_series = y_pred.get("priorities_number")
    for i in range(pr_number_series.__len__()):
        print(str(i) + "   pr_number_series   " + str(pr_number_series[i]))
        print(str(i) + "  y_pred    " + str(y_pred_series[i]))
        module_result[pr_number_series[i]] = y_pred_series[i]
    return module_result


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name ="phoenix"#"helix"#"terraform"#"Ipython"#"kuma"#"incubator-heron"#"Katello"#"zipkin"#"incubator-heron"
    # ranklib所能调的库
    alg_name = "bayesian_network"
    # 测试模型性能的文件路径
    file_path = "../data_processing_engineering/bayesian_data/" + repo_name + "/"
    path_exists_or_create(file_path)
    origin_data_path = file_path + repo_name + "_bayes_rank_format_test_data.csv"
    bayesian_result_path = "./result/bayesian_network/" + repo_name + "/"
    path_exists_or_create(bayesian_result_path)
    result_path = bayesian_result_path + repo_name + "_" + alg_name + "_result.csv"
    # 训练模型的文件路径
    train_data_path = file_path + repo_name + "_bayes_rank_format_train_data.csv"
    test_data_path = file_path + repo_name + "_bayes_rank_format_test_data.csv"

    # 首先运行算法训练模型,并得到其在测试集上的结果
    result_rate_in_dict = train_model_and_result(alg_name, train_data_path, test_data_path, repo_name)
    print(alg_name + "模型训练完成==========")
    for key in result_rate_in_dict.keys():
        print(str(key) + "....." + str(result_rate_in_dict.get(key)))
    day_data, response_time, first_response_time_dict, pr_number_index_dict = get_data_by_repo_name_and_origin_data_path(
        origin_data_path, repo_name)
    true_rate_label_dict = get_true_order_dict(response_time, first_response_time_dict)
    alg_model_result(true_rate_label_dict, day_data, pr_number_index_dict, result_rate_in_dict, result_path)

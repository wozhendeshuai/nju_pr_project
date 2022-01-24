import data_processing_engineering.get_data_from_database.database_connection as dbConnection
from baseline.true_order import get_true_order_dict
import pandas as pd
from utils.date_utils.date_function import is_weekday_commit \
    , project_age, get_latency_after_response, get_waiting_time, get_close_pr_time
from utils.num_utils.num_function import get_label_count \
    , get_workload, get_prev_prs, get_change_num \
    , get_accept_num, get_close_num, get_review_num \
    , get_participants_count
from utils.str_utils.str_function import wordCount
from utils.num_utils.num_ratio_function import get_pr_author_rate \
    , get_project_line_rate, get_line_weekday_rate, get_project_line_churn_rate \
    , get_commits_average, get_avg_comments, get_avg_latency
import os
import csv


# all_filename保存的是全集数据，train_filename,保存的是训练数据，test_filename保存的是测试数据，data为要写入数据列表.
def text_save(all_filename, data):  # filename为写入CSV文件的路径，data为要写入数据列表.
    all_file = open(all_filename, 'w+')
    data_len = len(data)
    train_len = int(data_len * 0.8)
    for i in range(data_len):
        s = str(data[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
        s = s.replace("'", '').replace(',', '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符

        all_file.write(s)
    all_file.close()
    print("保存文件成功")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name = "salt"  # "zipkin"#"angular.js"  # "tensorflow"  # "symfony"# #"spring-boot"#"spring-framework"#"rails"
    file_path = "./result/bayesian_network/" + repo_name + "/" + repo_name + "_bayesian_network_result.csv"
    temp = pd.read_csv(file_path)
    temp_ndcg = temp.get("ndcg")
    temp_mrr = temp.get("mrr")
    temp_kendall_tau_distance = temp.get("kendall_tau_distance")
    temp_ndcg_mean = temp_ndcg.mean()
    temp_mrr_mean = temp_mrr.mean()
    temp_kendall_tau_distance_mean = temp_kendall_tau_distance.mean()

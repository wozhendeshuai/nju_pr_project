import csv

import pandas as pd

# all_filename保存的是全集数据，train_filename,保存的是训练数据，test_filename保存的是测试数据，data为要写入数据列表.
from utils.path_exist import path_exists_or_create


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


def get_mean(file_path):
    temp = pd.read_csv(file_path)
    temp_ndcg = temp.get("ndcg")
    temp_mrr = temp.get("mrr")
    temp_kendall_tau_distance = temp.get("kendall_tau_distance")
    temp_ndcg_mean = temp_ndcg.mean()
    temp_mrr_mean = temp_mrr.mean()
    temp_kendall_tau_distance_mean = temp_kendall_tau_distance.mean()
    return temp_ndcg_mean, temp_mrr_mean, temp_kendall_tau_distance_mean


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name = "opencv"#"terraform"#"phoenix"#"helix"#"Ipython"#"kuma"#"incubator-heron"#"zipkin"#"Katello"
    file_path_tmp = []
    alg_dict = {
        0: "MART",
        1: "RankNet",
        2: "RankBoost",
        3: "AdaRank",
        4: "Coordinate_Ascent",
        6: "LambdaMART",
        7: "ListNet",
        8: "Random_Forests"
    }
    for alg_index in alg_dict.keys():
        alg_name = alg_dict.get(alg_index)
        ranklib_file_path = "./result/ranklib/" + repo_name + "/" + repo_name + "_" + alg_name + "_result.csv"
        file_path_tmp.append(ranklib_file_path)
    bayesian_network_file_path = "./result/bayesian_network/" + repo_name + "/" + repo_name + "_bayesian_network_result.csv"
    fifo_file_path = "./result/fifo/" + repo_name + "_FIFO_result.csv"
    xgboost_file_path = "./result/xgboost/" + repo_name + "/" + repo_name + "_xgboost_result.csv"
    small_file_path = "./result/small_size_first/" + repo_name + "_small_size_first_result.csv"
    file_path_tmp.append(xgboost_file_path)
    file_path_tmp.append(bayesian_network_file_path)
    file_path_tmp.append(fifo_file_path)
    file_path_tmp.append(small_file_path)

    row_data = []
    for index in range(file_path_tmp.__len__()):
        tmp = []
        temp_path = file_path_tmp[index]
        temp_ndcg_mean, temp_mrr_mean, temp_kendall_tau_distance_mean = get_mean(temp_path)
        tmp.append(temp_path)
        tmp.append(temp_ndcg_mean)
        tmp.append(temp_mrr_mean)
        tmp.append(temp_kendall_tau_distance_mean)
        row_data.append(tmp)
    headers = ['file_path',
               'ndcg_mean',
               'mrr_mean',
               'kendall_tau_distance_mean'
               ]
    # 保存数据到csv文件
    result_path = "./result/total/" + repo_name + "/"
    path_exists_or_create(result_path)
    with open(result_path + repo_name + "_total_result.csv",
              'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in row_data:
            writer.writerow(item)

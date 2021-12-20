'''
获取到所有的PR信息，找出每一个PR创建的时间，以及在该PR创建时间那个时刻仍处于open状态的pr，
然后将这个时刻还处于open状态的pr作为输入X。
FIFO算法，根据pr创建的时间先创建，放在最前面，这样对上述pr列表进行排序。FIFOY
真实排序：在该时刻之后，该X中，被相应，或者被关闭或者被合并等发生改变的时间，根据该时间顺序进行排序，进而获取真实排序TRUEY
将FIFOY，与TRUEY进行比较，通过NDGC进行比较，判断排序效果
'''
import data_processing_engineering.get_data_from_database.database_connection as dbConnection
from baseline.true_order import get_true_order_dict
from utils.date_utils.date_function import get_waiting_time
import csv
from evaluation_index.ndgc import ndcg
# Python的标准库linecache模块非常适合这个任务
import linecache
import os

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

repo_name = "angular.js"  # "symfony"# #"tensorflow"#"spring-boot"#"spring-framework"#"rails"
# 文件路径
jar_path = "E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar"
origin_data_path = "E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\" + repo_name + "_svm_rank_format_data.txt"
temp_data_path = "E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\" + repo_name + "temp_svm_rank_format_data.txt"
temp_sort_result_path = "E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\" + repo_name + "_myScoreFile.txt"
model_path = "E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\" + repo_name + "_randomforest_model.txt"


def get_data_by_repo_name():
    data = dbConnection.getDataFromSql(
        "select * from pr_self where repo_name='" + repo_name + "' and closed_at is not null order by pr_number")

    print(len(data))  ##查看PR数量

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
    first_response_time_dict = get_waiting_time(first_response_time_dict)
    # print(first_response_time_dict)
    # 响应时间 按照pr_number的顺序进行排列
    response_time = []
    for item in first_response_time_dict.keys():
        response_time.append(first_response_time_dict[item])
    return day_data, response_time, first_response_time_dict, pr_number_index_dict


def prepare_temp_file(temp_data_path, origin_data_path, open_pr_index_list, day):
    file = open(temp_data_path, 'w+')
    for i in range(len(open_pr_index_list)):
        s = getline(origin_data_path, open_pr_index_list[i]+1)
        # s = s.replace("'", '').replace(',', '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()
    print("保存第 "+str(day)+" 天的临时文件成功")


# 可显示使用循环, 注意enumerate从0开始计数，而line_number从1开始
def getline(the_file_path, line_number):
    if line_number < 1:
        return ''
    for cur_line_number, line in enumerate(open(the_file_path, 'rU')):
        if cur_line_number == line_number - 1:
            return line
    return ''


# 从模型计算出的排序文件获取模型的排序结果
def get_result_list(the_file_path):
    result = []
    for line in open(the_file_path):
        line_str = line.split(" ")
        result.append(int(line_str[2]))
    return result


# 根据已有数据得到排序结果
def random_forest(day_data, day, pr_number_index_dict):
    re_rank_str = "java -jar " + jar_path + " -load " + model_path + " -rank " + temp_data_path + " -indri " + temp_sort_result_path
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
                if temp_pr_dict[pr_key]['closed_time'].date() < day:
                    continue
                else:
                    open_pr_list.append(pr_key)
                    open_pr_index_list.append(pr_number_index_dict.get(pr_key))
    prepare_temp_file(temp_data_path, origin_data_path, open_pr_index_list, day)
    recv = os.popen(re_rank_str)
    print("模型计算中：")
    print(recv.read())
    sort_result = get_result_list(temp_sort_result_path)
    return sort_result


# 对fifo进行调用，同时将数据写入到文件中，方便后续统计
def random_forest_result(true_rate_label_dict, day_data, pr_number_index_dict):
    ndgc_list = []
    day_list = []
    max_day = None
    min_day = None
    for day in day_data.keys():
        print("=================================日期:", day)
        # 获取每一天还处于open状态的pr列表顺序
        sort_result = random_forest(day_data, day, pr_number_index_dict)
        rank_sort = []
        true_sort = []
        # 获取从fifo中获取的每个列表的顺序
        for pr_number_result in sort_result:
            rank_sort.append(true_rate_label_dict[pr_number_result])
            true_sort.append(true_rate_label_dict[pr_number_result])
        true_sort.sort(reverse=True)
        ndcg_num = ndcg(true_sort, rank_sort, rank_sort.__len__())
        print("pr_number排序:", sort_result)
        print("rank_sort:", rank_sort)
        print("true_sort:", true_sort)
        print("ndgc_num:", ndcg_num)
        if max_day is None or max_day < day:
            max_day = day
        if min_day is None or min_day > day:
            min_day = day
        day_list.append(day)
        ndgc_list.append(ndcg_num)

    headers = ['日期',
               'ndgc'
               ]
    row_data = []
    for i in range(len(day_list)):
        tmp = []
        tmp.append(day_list[i])
        tmp.append(ndgc_list[i])
        row_data.append(tmp)
    print(row_data)
    # 保存数据到csv文件
    with open("./result/rankLib/" + repo_name + "_random_forest_result.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in row_data:
            writer.writerow(item)
    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    day_data, response_time, first_response_time_dict, pr_number_index_dict = get_data_by_repo_name()
    true_rate_label_dict = get_true_order_dict(response_time, first_response_time_dict)
    random_forest_result(true_rate_label_dict, day_data, pr_number_index_dict)

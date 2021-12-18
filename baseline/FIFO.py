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


def get_data_by_repo_name(repo_name):
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

    first_response_time_dict = dict(first_response_time)
    first_response_time_dict = get_waiting_time(first_response_time_dict)
    # print(first_response_time_dict)
    # 响应时间 按照pr_number的顺序进行排列
    response_time = []
    for item in first_response_time_dict.keys():
        response_time.append(first_response_time_dict[item])
    return day_data, response_time, first_response_time_dict


# print(response_time)
# 根据已有数据得到FIFO的排序结果
def fifo(day_data, day):
    fifo_data = []
    # 得到本日以及本日之前还处于开放状态的pr，并按照先进先出对pr_number进行排序
    for key in day_data.keys():
        if key > day:
            continue
        else:
            # 获取当前天的所有PR
            temp_pr_dict = day_data[key]
            for pr_key in temp_pr_dict:
                if temp_pr_dict[pr_key]['closed_time'].date() < day:
                    continue
                else:
                    fifo_data.append(pr_key)
    return fifo_data


def fifo_result(true_rate_label_dict, day_data, repo_name):
    ndgc_list = []
    day_list = []
    max_day = None
    min_day = None
    for day in day_data.keys():
        fifo_data = fifo(day_data, day)
        fifo_sort = []
        true_sort = []
        # 获取从fifo中获取的每个列表的顺序
        for pr_number_fifo in fifo_data:
            fifo_sort.append(true_rate_label_dict[pr_number_fifo])
            true_sort.append(true_rate_label_dict[pr_number_fifo])
        true_sort.sort(reverse=True)
        ndcg_num = ndcg(true_sort, fifo_sort, fifo_sort.__len__())
        print("=================================日期:", day)
        print("fifo pr_number排序:", fifo_data)
        print("fifo_sort:", fifo_sort)
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
    count = 0
    for i in range(len(day_list)):
        tmp = []
        tmp.append(day_list[i])
        tmp.append(ndgc_list[i])
        row_data.append(tmp)
    print(row_data)
    # 保存数据到csv文件
    with open("./" + repo_name + "_FIFO_result.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(headers)
        for item in row_data:
            writer.writerow(item)
    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name = "spring-boot"
    day_data, response_time, first_response_time_dict = get_data_by_repo_name(repo_name)
    true_rate_label_dict = get_true_order_dict(response_time, first_response_time_dict)
    fifo_result(true_rate_label_dict, day_data, repo_name)

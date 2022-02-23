'''
获取到所有的PR信息，找出每一个PR创建的时间，以及在该PR创建时间那个时刻仍处于open状态的pr，
然后将这个时刻还处于open状态的pr作为输入X。
FIFO算法，根据pr创建的时间先创建，放在最前面，这样对上述pr列表进行排序。FIFOY
真实排序：在该时刻之后，该X中，被相应，或者被关闭或者被合并等发生改变的时间，根据该时间顺序进行排序，进而获取真实排序TRUEY
将FIFOY，与TRUEY进行比较，通过NDGC进行比较，判断排序效果
'''
import data_processing_engineering.get_data_from_database.database_connection as dbConnection
from baseline.true_order import get_true_order_dict

from utils.date_utils.date_function import is_weekday_commit \
    , project_age, get_latency_after_response, get_waiting_time, get_close_pr_time
from utils.num_utils.num_function import get_label_count \
    , get_workload, get_prev_prs, get_change_num \
    , get_accept_num, get_close_num, get_review_num \
    , get_participants_count
from utils.path_exist import path_exists_or_create
from utils.str_utils.str_function import wordCount
from utils.num_utils.num_ratio_function import get_pr_author_rate \
    , get_project_line_rate, get_line_weekday_rate, get_project_line_churn_rate \
    , get_commits_average, get_avg_comments, get_avg_latency
import csv

# 增加代码的可读性
pr_number_index = 0
repo_name_index = 1
pr_user_id_index = 2
pr_author_association_index = 3
labels_index = 4
created_at_index = 5
closed_at_index = 6
merged_at_index = 7
merged_index = 8
mergeable_state_index = 9
assignees_content_index = 10
comments_number_index = 11
comments_content_index = 12
review_comments_number_index = 13
review_comments_content_index = 14
commit_number_index = 15
changed_file_num_index = 16
total_add_line_index = 17
total_delete_line_index = 18
pr_user_name_index = 19
pr_id_index = 20
updated_at_index = 21
content_index = 22
title_index = 23
body_index = 24


# all_filename保存的是全集数据，train_filename,保存的是训练数据，test_filename保存的是测试数据，data为要写入数据列表.
def text_save(all_filename, train_filename, test_filename, data, headers):  # filename为写入CSV文件的路径，data为要写入数据列表.
    all_file = open(all_filename, 'w', encoding='utf-8', newline='')
    train_file = open(train_filename, 'w', encoding='utf-8', newline='')
    test_file = open(test_filename, 'w', encoding='utf-8', newline='')
    all_file_writer = csv.writer(all_file, dialect='excel')
    train_file_writer = csv.writer(train_file, dialect='excel')
    test_file_writer = csv.writer(test_file, dialect="excel")
    all_file_writer.writerow(headers)
    train_file_writer.writerow(headers)
    test_file_writer.writerow(headers)

    data_len = len(data)
    train_len = int(data_len * 0.8)
    for i in range(data_len):
        all_file_writer.writerow(data[i])
        if i <= train_len:
            train_file_writer.writerow(data[i])
        else:
            test_file_writer.writerow(data[i])
    all_file.close()
    train_file.close()
    test_file.close()
    print("保存文件成功")


def get_data_by_repo_name(repo_name):
    # 从数据库获取数据
    raw_data = dbConnection.getDataFromSql(
        "select * from pr_self where repo_name='" + repo_name + "' and closed_at is not null order by pr_number")

    print(len(raw_data))  ##查看PR数量

    # 标记有用的PR自身信息的下标
    useful_features_index = [0,  ##pr_number
                             2,  ##repo_name
                             3,  ##pr_user_id
                             5,  ##pr_author_association
                             8,  ##labels
                             10,  ##created_at
                             12,  ##closed_at
                             13,  ##merged_at
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
                             4,  ##pr_user_name
                             11,  ##updated_at
                             6,  ##title
                             7,  ##body
                             ]

    selected_data = []  ##保留有用的属性特征
    for item in raw_data:
        tmp = []
        for i in useful_features_index:
            tmp.append(item[i])
        selected_data.append(tmp)

    process_data = []
    count = 0
    for item in selected_data:
        tmp = []
        ##pr_number
        tmp.append(item[0])
        ##repo_name
        tmp.append(item[1])
        ##pr_user_id
        tmp.append(item[2])
        ####pr_author_association
        if item[3] == 'CONTRIBUTOR':
            tmp.append(0)
        elif item[3] == 'MEMBER':
            tmp.append(1)
        elif item[3] == 'NONE':
            tmp.append(2)
        else:
            tmp.append(3)

        ##labels
        if item[4] == '{}':
            tmp.append(0)
        else:
            tmp.append(1)

        ##created_at
        tmp.append(item[5])
        ##closed_at
        tmp.append(item[6])
        ##merged_at
        tmp.append(item[7])

        ##merged
        tmp.append(item[8])

        ##mergeable_state
        if item[9] == 'unknown':
            tmp.append(0)
        elif item[9] == 'blocked':
            tmp.append(1)
        elif item[9] == 'dirty':
            tmp.append(2)
        else:
            tmp.append(3)

        ##assignees_content
        if item[10] == '{}':
            tmp.append(0)
        else:
            tmp.append(1)

        ##comments_number
        tmp.append(item[11])

        ##comments_content
        tmp.append(item[12])
        ##review_comments_number
        tmp.append(item[13])
        ##review_comments_content
        tmp.append(item[14])
        ##commit_number
        tmp.append(item[15])
        ##changed_file_num
        tmp.append(item[16])
        ##total_add_line
        tmp.append(item[17])
        ##total_delete_line
        tmp.append(item[18])

        ##pr_username
        tmp.append(item[19])

        ##pr_id
        tmp.append(count)

        ##updated_at
        tmp.append(item[20])

        ##content
        tmp.append(item[4])

        ##title
        tmp.append(item[21])

        ##body
        tmp.append(item[22])

        count += 1
        process_data.append(tmp)

    print(count)

    ##获得仓库年龄
    repo_data = dbConnection.getDataFromSql(
        "select repo_id,repo_name\
            ,project_created_at,project_updated_at\
            ,project_pushed_at from pr_repo"
    )

    repo_id_index = 0
    repo_data_name_index = 1
    project_created_at_index = 2
    project_updated_at_index = 3
    project_pushed_at_index = 4

    proj_age = []
    for item in repo_data:
        tmp = []
        tmp.append(('created_time', item[project_created_at_index]))
        tmp.append(('updated_time', item[project_updated_at_index]))
        tmp.append(('pushed_time', item[project_pushed_at_index]))
        tmp = dict(tmp)
        proj_age.append((item[repo_id_index], tmp))

    proj_age = dict(proj_age)
    proj_age = project_age(proj_age)

    Proj_age = []
    for item in process_data:
        for i in repo_data:
            if item[repo_name_index] == i[repo_data_name_index]:
                Proj_age.append(proj_age[i[repo_id_index]])

    ##是否为工作日
    is_weekday = []
    for item in process_data:
        is_weekday.append((item[pr_id_index], item[created_at_index]))
    is_weekday = dict(is_weekday)
    is_weekday = is_weekday_commit(is_weekday)

    ###获取PR的label数
    label_dict = []
    for item in process_data:
        label_dict.append((item[pr_id_index], item[content_index]))
    label_dict = dict(label_dict)
    label_dict = get_label_count(label_dict)

    ##获取每个PR提交时，open PR的数量
    workload = []
    for item in process_data:
        tmp = []
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp = dict(tmp)
        workload.append((item[pr_id_index], tmp))

    workload = dict(workload)
    workload = get_workload(workload)

    # 获取该pr提交之前，提交者提交的pr数量

    pre_prs = []
    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp = dict(tmp)
        pre_prs.append((item[pr_id_index], tmp))

    pre_prs = dict(pre_prs)
    pre_prs = get_prev_prs(pre_prs)

    # 获取该pr提交之前，提交者提交的pr中的代码更改总数
    change_num = []
    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('changed_line_num', item[total_add_line_index] + item[total_delete_line_index]))
        tmp = dict(tmp)
        change_num.append((item[pr_id_index], tmp))

    change_num = dict(change_num)
    change_num = get_change_num(change_num)

    # 获取该pr提交之前，提交者提交的pr的接受总数
    accept_num = []
    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('merged_at', item[merged_at_index]))
        tmp = dict(tmp)
        accept_num.append((item[pr_id_index], tmp))

    accept_num = dict(accept_num)
    accept_num = get_accept_num(accept_num)

    # 获取该pr提交之前，提交者提交的pr的关闭总数
    close_num = []

    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp.append(('merged_at', item[merged_at_index]))
        tmp = dict(tmp)
        close_num.append((item[pr_id_index], tmp))

    close_num = dict(close_num)
    close_num = get_close_num(close_num)

    # 该pr作者之前评审过多少pr review_comments
    review_num = []

    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp.append(('review_comments_number', item[review_comments_number_index]))
        tmp.append(('review_comments_content', item[review_comments_content_index]))
        tmp = dict(tmp)
        review_num.append((item[pr_id_index], tmp))

    review_num = dict(review_num)
    review_num = get_review_num(review_num)

    # 获取该pr的参与者之和，包括提交者，评论者，评审者人数
    participants_count = []
    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp.append(('comments_number', item[comments_number_index]))
        tmp.append(('comments_content', item[comments_content_index]))
        tmp.append(('review_comments_number', item[review_comments_number_index]))
        tmp.append(('review_comments_content', item[review_comments_content_index]))
        tmp = dict(tmp)
        participants_count.append((item[pr_id_index], tmp))

    participants_count = dict(participants_count)
    participants_count = get_participants_count(participants_count)

    title_words = []
    for item in process_data:
        title_words.append(wordCount(item[title_index]))

    body_words = []
    for item in process_data:
        body_words.append(wordCount(item[body_index]))

    key_words = ['bug', 'document', 'feature', 'improve', 'refactor']
    has_key_words = []
    for item in process_data:
        tmp = []
        if item[body_index] is None:
            tmp = [0, 0, 0, 0, 0]
        else:
            for k in key_words:
                if k in item[body_index]:
                    tmp.append(1)
                else:
                    tmp.append(0)
        has_key_words.append(tmp)

    #  获取pr作者在代码仓的总提交成功率,接受概率，总的贡献给率，代码仓的贡献率

    pr_data = []
    for item in process_data:
        tmp = []
        tmp.append(('pr_user_name', item[pr_user_name_index]))
        tmp.append(('created_time', item[created_at_index]))
        tmp.append(('closed_time', item[closed_at_index]))
        tmp.append(('comments_number', item[comments_number_index]))
        tmp.append(('comments_content', item[comments_content_index]))
        tmp.append(('review_comments_number', item[review_comments_number_index]))
        tmp.append(('review_comments_content', item[review_comments_content_index]))
        tmp.append(('total_add_line', item[total_add_line_index]))
        tmp.append(('total_delete_line', item[total_delete_line_index]))
        tmp.append(('commit_number', item[commit_number_index]))
        tmp.append(('merged_time', item[merged_at_index]))
        tmp = dict(tmp)
        pr_data.append((item[pr_id_index], tmp))

    pr_data = dict(pr_data)

    # #  获取pr作者在代码仓的总提交成功率,接受概率，总的贡献给率，代码仓的贡献率
    # pr_author_rate = get_pr_author_rate(pr_data)
    #
    # # 获取project上一周的平均删除，增加，改变的行的数量
    # project_line_rate = get_project_line_rate(pr_data)
    #
    # # 计算pr根据所在周的周几，判断该周几的平均修改的行数，增加的数量，删除的数量
    # line_weekday_rate = get_line_weekday_rate(pr_data)
    #
    # # 获取pr的平均删除，增加，改变的行的数量,不是一周一个单位了，而是pr的数量
    # project_line_churn_rate = get_project_line_churn_rate(pr_data)
    #
    # # 根据当前pr创建的时间，计算所有pr的平均提交数量
    # commits_average = get_commits_average(pr_data)
    #
    # # 根据当前pr创建的时间，计算所有pr的平均评论数，以及合并的pr的平均评论数
    # avg_comments = get_avg_comments(pr_data)
    #
    # # 计算pr的合并时间，计算，从pr的打开状态到合并状态的平均天数，以及从打开状态到关闭状态的平均天数
    # avg_latency = get_avg_latency(pr_data)

    X_dispersed = []  ##离散类型值
    X_successive = []  ##连续类型值

    for item in process_data:
        X_dispersed.append(
            [item[pr_number_index], item[pr_author_association_index], item[labels_index], item[mergeable_state_index]
                , item[assignees_content_index]])

    comments_number_tmp = []
    comments_number_dict = {}
    review_comments_number_tmp = []
    review_comments_number_dict = {}
    commit_number_tmp = []
    commit_number_dict = {}
    changed_file_num_tmp = []
    changed_file_num_dict = {}
    total_add_line_tmp = []
    total_add_line_dict = {}
    total_delete_line_tmp = []
    total_delete_line_dict = {}

    for item in process_data:
        # 将下面数据全部5等分，方便贝叶斯计算
        comments_number_tmp.append(item[comments_number_index])
        comments_number_dict[item[pr_number_index]] = item[comments_number_index]
        review_comments_number_tmp.append(item[review_comments_number_index])
        review_comments_number_dict[item[pr_number_index]] = item[review_comments_number_index]
        commit_number_tmp.append(item[commit_number_index])
        commit_number_dict[item[pr_number_index]] = item[commit_number_index]
        changed_file_num_tmp.append(item[changed_file_num_index])
        changed_file_num_dict[item[pr_number_index]] = item[changed_file_num_index]
        total_add_line_tmp.append(item[total_add_line_index])
        total_add_line_dict[item[pr_number_index]] = item[total_add_line_index]
        total_delete_line_tmp.append(item[total_delete_line_index])
        total_delete_line_dict[item[pr_number_index]] = item[total_delete_line_index]
        # X_successive.append([item[comments_number_index], item[review_comments_number_index], item[commit_number_index]
        #                         , item[changed_file_num_index], item[total_add_line_index],
        #                      item[total_delete_line_index]])
    # 将下面数据全部5等分，方便贝叶斯计算
    true_comments_number_dict = get_true_order_dict(comments_number_tmp, comments_number_dict)
    true_review_comments_number_dict = get_true_order_dict(review_comments_number_tmp, review_comments_number_dict)
    true_commit_number_dict = get_true_order_dict(commit_number_tmp, commit_number_dict)
    true_changed_file_num_dict = get_true_order_dict(changed_file_num_tmp, changed_file_num_dict)
    true_total_add_line_dict = get_true_order_dict(total_add_line_tmp, total_add_line_dict)
    true_total_delete_line_dict = get_true_order_dict(total_delete_line_tmp, total_delete_line_dict)

    for key_temp in true_comments_number_dict.keys():
        X_successive.append([true_comments_number_dict.get(key_temp), true_review_comments_number_dict.get(key_temp),
                             true_commit_number_dict.get(key_temp)
                                , true_changed_file_num_dict.get(key_temp), true_total_add_line_dict.get(key_temp),
                             true_total_delete_line_dict.get(key_temp)])
    for i in range(len(X_dispersed)):
        # X_dispersed[i].append(pr_author_rate[i]['self_accept_rate'])
        # X_dispersed[i].append(pr_author_rate[i]['self_closed_num_rate'])
        # X_dispersed[i].append(pr_author_rate[i]['self_contribution_rate'])
        # X_dispersed[i].append(pr_author_rate[i]['project_accept_rate'])
        X_dispersed[i].append(is_weekday[i])
    label_count_tmp = []
    workload_tmp = []
    pre_prs_tmp = []
    change_num_tmp = []
    accept_num_tmp = []
    close_num_tmp = []
    review_num_tmp = []
    participants_count_tmp = []
    title_words_tmp = []
    title_words_dict = {}
    body_words_tmp = []
    body_words_dict = {}
    for i in range(len(X_successive)):
        label_count_tmp.append(label_dict[i])
        workload_tmp.append(workload[i])
        pre_prs_tmp.append(pre_prs[i])
        change_num_tmp.append(change_num[i])
        accept_num_tmp.append(accept_num[i])
        close_num_tmp.append(close_num[i])
        review_num_tmp.append(review_num[i])
        participants_count_tmp.append(participants_count[i])
        title_words_tmp.append(title_words[i])
        title_words_dict[i] = title_words[i]
        body_words_tmp.append(body_words[i])
        body_words_dict[i] = body_words[i]
    true_label_count_dict = get_true_order_dict(label_count_tmp, label_dict)
    true_workload_dict = get_true_order_dict(workload_tmp, workload)
    true_pre_prs_dict = get_true_order_dict(pre_prs_tmp, pre_prs)
    true_change_num_dict = get_true_order_dict(change_num_tmp, change_num)
    true_accept_num_dict = get_true_order_dict(accept_num_tmp, accept_num)
    true_close_num_dict = get_true_order_dict(close_num_tmp, close_num)
    true_review_num_dict = get_true_order_dict(review_num_tmp, review_num)
    true_participants_count_dict = get_true_order_dict(participants_count_tmp, participants_count)
    true_title_words_dict = get_true_order_dict(title_words_tmp, title_words_dict)
    true_body_words_dict = get_true_order_dict(body_words_tmp, body_words_dict)

    for i in range(len(X_successive)):
        X_successive[i].append(true_label_count_dict[i])
        X_successive[i].append(true_workload_dict[i])
        X_successive[i].append(true_pre_prs_dict[i])
        X_successive[i].append(true_change_num_dict[i])
        X_successive[i].append(true_accept_num_dict[i])
        X_successive[i].append(true_close_num_dict[i])
        X_successive[i].append(true_review_num_dict[i])
        X_successive[i].append(true_participants_count_dict[i])
        X_successive[i].append(true_title_words_dict[i])
        X_successive[i].append(true_body_words_dict[i])
        for k in has_key_words[i]:
            X_successive[i].append(k)

        # X_successive[i].append(project_line_rate[i]['deletions_per_week'])
        # X_successive[i].append(project_line_rate[i]['additions_per_week'])
        # X_successive[i].append(project_line_rate[i]['changes_per_week'])
        # X_successive[i].append(line_weekday_rate[i]['per_lines_deleted_week_days'])
        # X_successive[i].append(line_weekday_rate[i]['per_lines_added_week_days'])
        # X_successive[i].append(line_weekday_rate[i]['per_lines_changed_week_days'])
        # X_successive[i].append(project_line_churn_rate[i]['deletions_per_pr'])
        # X_successive[i].append(project_line_churn_rate[i]['additions_per_pr'])
        # X_successive[i].append(project_line_churn_rate[i]['changes_per_pr'])
        # X_successive[i].append(commits_average[i])
        # X_successive[i].append(avg_comments[i]['comments_per_closed_pr'])
        # X_successive[i].append(avg_comments[i]['comments_per_merged_pr'])
        # X_successive[i].append(avg_latency[i]['close_latency'])
        # X_successive[i].append(avg_latency[i]['merge_latency'])
    #
    # ###归一化
    # X_successive = np.array(X_successive)
    # mins = X_successive.min(0)  # 返回data矩阵中每一列中最小的元素，返回一个列表
    # maxs = X_successive.max(0)  # 返回data矩阵中每一列中最大的元素，返回一个列表
    # ranges = maxs - mins  # 最大值列表 - 最小值列表 = 差值列表
    # normData = np.zeros(np.shape(X_successive))  # 生成一个与 data矩阵同规格的normData全0矩阵，用于装归一化后的数据
    # row = X_successive.shape[0]  # 返回 data矩阵的行数
    # normData = X_successive - np.tile(mins, (row, 1))  # data矩阵每一列数据都减去每一列的最小值
    # normData = normData / np.tile(ranges, (row, 1))
    # X_successive = normData.tolist()

    X = []
    for i in range(len(X_dispersed)):
        tmp = []
        for j in range(1, len(X_dispersed[i])):
            tmp.append(X_dispersed[i][j])
        for j in X_successive[i]:
            tmp.append(j)
        X.append((X_dispersed[i][0], tmp))
    X_dict = dict(X)
    ##获取每个PR的响应时间
    first_response_time = []
    for item in process_data:
        tmp = []
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

    first_response_time = dict(first_response_time)
    first_response_time = get_close_pr_time(first_response_time)  # get_waiting_time(first_response_time)

    ##响应时间
    Y1 = []
    for item in first_response_time.keys():
        Y1.append(first_response_time[item])
    # 这里计算每个prNumber对应的真实速度编号
    true_rate_label_dict = get_true_order_dict(Y1, first_response_time)

    # ####响应时间
    # Y_1 = []
    # for item in Y1:
    #     Y_1.append(item)
    # ##是否被合并  (70%)
    # Y_2 = []
    # for item in process_data:
    #     Y_2.append(item[8])
    #
    # ##最终的输出label [快/慢响应，是/否合并]
    # Y = []
    # for i in range(0, len(Y_1)):
    #     Y.append([Y_1[i], Y_2[i]])

    row_data = []

    for key_item in true_rate_label_dict.keys():
        tmp = []
        tmp.append(str(key_item))
        tmp.append(true_rate_label_dict.get(key_item))
        for x in X_dict.get(key_item):
            tmp.append(str(x))
        row_data.append(tmp)
    return row_data


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repo_name ="dubbo"#"react"#"tensorflow"#"opencv"#"phoenix"#"helix"#"terraform"#"Ipython"#"kuma"#"incubator-heron"# "kuma"#"Katello"#"zipkin"#"yii2"
    file_path = "./bayesian_data/" + repo_name + "/"
    path_exists_or_create(file_path)
    all_filename = file_path + repo_name + "_bayes_rank_format_data.csv"
    train_filename = file_path + repo_name + "_bayes_rank_format_train_data.csv"
    test_filename = file_path + repo_name + "_bayes_rank_format_test_data.csv"
    row_data = get_data_by_repo_name(repo_name)
    headers = ['pr_number',
               'priorities_number',
               'author_identity',
               'has_labels',
               'mergable_state',
               'has_assignees_content',
               'is_weekday',
               'comment_num',
               'review_comment_num',
               'commit_num',
               'file_changed_num',
               'total_add_line',
               'total_delete_line',
               'label_count',
               'workload',
               'pre_prs',
               'change_num',
               'accept_num',
               'close_num',
               'review_num',
               'participants_count',
               'title_words',
               'body_words',
               'has_bug',
               'has_document',
               'has_feature',
               'has_improve',
               'has_refactor',
               # 'deletions_per_week',
               # 'additions_per_week',
               # 'changes_per_week',
               # 'per_lines_deleted_week_days',
               # 'per_lines_added_week_days',
               # 'per_lines_changed_week_days',
               # 'deletions_per_pr',
               # 'additions_per_pr',
               # 'changes_per_pr',
               # 'commits_average',
               # 'comments_per_closed_pr',
               # 'comments_per_merged_pr',
               # 'close_latency',
               # 'merge_latency'
               # 'self_accept_rate',
               # 'self_closed_num_rate',
               # 'self_contribution_rate',
               # 'project_accept_rate',
               ]
    text_save(all_filename, train_filename, test_filename, row_data, headers)

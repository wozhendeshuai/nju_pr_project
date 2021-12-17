'''
获取到所有的PR信息，找出每一个PR创建的时间，以及在该PR创建时间那个时刻仍处于open状态的pr，
然后将这个时刻还处于open状态的pr作为输入X。
FIFO算法，根据pr创建的时间先创建，放在最前面，这样对上述pr列表进行排序。FIFOY
真实排序：在该时刻之后，该X中，被相应，或者被关闭或者被合并等发生改变的时间，根据该时间顺序进行排序，进而获取真实排序TRUEY
将FIFOY，与TRUEY进行比较，通过NDGC进行比较，判断排序效果
'''
import data_processing_engineering.get_data_from_database.database_connection as dbConnection

data = dbConnection.getDataFromSql("select * from pr_self where repo_name='spring-boot' order by pr_number")

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
for item in selected_data:
    print(item)

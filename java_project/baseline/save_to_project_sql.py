# Press the green button in the gutter to run the script.
import pymysql


# 保存模型在测试集的表现效果
def save_test_result_to_sql(train_day, repo_name, alg_name, test_day, ndcg, mrr, kendall_tau_distance):
    ##连接数据库
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,  # 端口号
        user="root",  # 数据库用户
        password="root",  # 数据库密码
        database="project_sort_db"  # 要连接的数据库名称
    )
    cursor = conn.cursor()  # 游标
    # 从数据库获取数据
    select_sql = """
            select *
            from alg_test_eval
            where train_day=%s and repo_name=%s and alg_name=%s and test_day = %s """
    select_data = (train_day, repo_name, alg_name, test_day)
    # print(select_sql)
    cursor.execute(select_sql, select_data)
    raw_data = cursor.fetchall()

    # 若今天还未插入数据则，走插入逻辑
    if raw_data.__len__() == 0:
        insert_sql = """
                insert into alg_test_eval(train_day,repo_name, alg_name,test_day,ndcg,mrr,kendall_tau_distance)
                VALUES( %s,%s,%s, %s,%s, %s,%s )
               """
        sqlData = (train_day, repo_name, alg_name, test_day, ndcg, mrr, kendall_tau_distance)
        # 执行sql语句
        cursor.execute(insert_sql, sqlData)
        print(sqlData, "数据插入成功")
        # 提交到数据库执行
        conn.commit()
    # 若今天已插入数据，则更新相关内容
    elif raw_data.__len__() > 0:
        update_sql = """
                       update  alg_test_eval set
                       ndcg= %s,mrr= %s,kendall_tau_distance= %s
                      where train_day=%s and repo_name=%s and alg_name=%s and test_day = %s 
                      """
        sqlData = (ndcg, mrr, kendall_tau_distance, train_day, repo_name, alg_name, test_day)
        # 执行sql语句
        cursor.execute(update_sql, sqlData)
        print(sqlData, "数据更新成功")
        # 提交到数据库执行
        conn.commit()
    conn.close()


# 保存模型计算的open状态的PR排序列表
def save_result_to_sql(data_time, repo_name, alg_name, sort_result):
    ##连接数据库
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,  # 端口号
        user="root",  # 数据库用户
        password="root",  # 数据库密码
        database="project_sort_db"  # 要连接的数据库名称
    )
    cursor = conn.cursor()  # 游标
    # 从数据库获取数据
    select_sql = "select * from alg_sort_result where repo_name='" + repo_name + "' and  sort_day='" + data_time + "' and alg_name='" + alg_name + "'"
    print(select_sql)
    cursor.execute(select_sql)
    raw_data = cursor.fetchall()

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
        delete_pr_numbers = []
        for temp_index in range(raw_data.__len__()):
            raw_data_pr_number_dict[raw_data[temp_index][3]] = temp_index
            # 判断是否有不在最新结果集的pr_number
            flag = False
            for i in range(sort_result.__len__()):
                if raw_data[temp_index][3] == sort_result[i]:
                    flag = True
                    break
            if flag is False:
                delete_pr_numbers.append(raw_data[temp_index][3])
        for temp_index in range(true_len):
            # 如果raw_data存在，则更新，否则就插入，如果结束之后，还是已存在的多，则删除多余的已存在的，如果是新的多，则已被插入
            pr_number_temp = sort_result[temp_index]
            if raw_data_pr_number_dict.__contains__(pr_number_temp):
                # 补齐更新语句
                update_sql_data = (temp_index, data_time, repo_name, alg_name, sort_result[temp_index])
                update_result_to_db(conn, cursor, update_sql_data)
            else:
                # 不在已有的结果集中可以插入
                insert_sql_data = (data_time, repo_name, alg_name, sort_result[temp_index], temp_index)
                insert_result_to_db(conn, cursor, insert_sql_data)

        for temp_index in range(delete_pr_numbers.__len__()):
            pr_number_temp = delete_pr_numbers[temp_index]
            delete_sql_data = (data_time, repo_name, alg_name, pr_number_temp)
            delete_result_to_db(conn, cursor, delete_sql_data)
    conn.close()


# 更新语句
def update_result_to_db(conn, cursor, sqlData):
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
def delete_result_to_db(conn, cursor, sqlData):
    updata_sql = """
        delete  from alg_sort_result 
        where sort_day=%s and repo_name=%s and alg_name=%s and pr_number=%s"""

    # 执行sql语句
    cursor.execute(updata_sql, sqlData)
    # 提交到数据库执行
    conn.commit()
    print(sqlData, "数据删除成功")


# 插入语句
def insert_result_to_db(conn, cursor, sqlData):
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

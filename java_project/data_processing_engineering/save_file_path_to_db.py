import time

import pymysql

from java_project.project_spider.database_operation import get_database_connection


def save_feature_file_path(file_name, file_type, file_to_alg_name, file_path, repo_name, create_time, create_user_name):
    # SQL语句书写
    select_sql = """
    select *
    from feature_file_path
    where file_name=%s and file_type=%s and  file_to_alg_name=%s and file_path=%s and  repo_name=%s and create_time=%s and create_user_name=%s
    """
    sql = """insert into feature_file_path(
           file_name,
           file_type,
           file_to_alg_name,
           file_path,
           repo_name,
           create_time,
           create_user_name
           )VALUES(%s,%s,%s,%s,%s,%s,%s) """
    sqlData = (file_name,
               file_type,
               file_to_alg_name,
               file_path,
               repo_name,
               create_time,
               create_user_name)
    database = get_database_connection()
    # database = db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='pr_second', charset='utf8')
    # 创建游标对象
    cursor = database.cursor()
    # 利用游标对象进行操作
    # 先查询下是否已有该路径，若有则直接返回便可
    cursor.execute(select_sql, sqlData)
    index_temp_data = cursor.fetchall()
    if index_temp_data.__len__() != 0:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "已有相关特征文件数据: ", file_path)
        return
    else:
        cursor.execute(sql, sqlData)
        # 提交到数据库执行
        database.commit()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "数据插入数据库成功: ", file_path)

import pymysql as db


# 将散落在各处的链接数据库的相关操作进行汇总
def get_database_connection():
    return db.connect(host='127.0.0.1', port=3306, user='root', password='root', db='project_data_collection_db',
                      charset='utf8')

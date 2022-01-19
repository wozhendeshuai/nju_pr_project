# 关闭数据库连接
import pymysql
from sshtunnel import SSHTunnelForwarder



import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder


def get_tunnel_ssh(config_dict):
    ssh_tunnel = SSHTunnelForwarder(ssh_address_or_host=(config_dict.get("ssh_ip"), config_dict.get("ssh_port")),
                                    ssh_username=config_dict.get("ssh_user"),
                                    ssh_password=config_dict.get("ssh_password", 'password'),
                                    remote_bind_address=(config_dict.get("ip"), config_dict.get("port")))
    ssh_tunnel.start()
    # ssh_tunnel.close()
    return ssh_tunnel


def get_mysql_conn():
    ssh_config = {
        'ip': '172.19.241.129',
        'port': 3306,
        'ssh_ip': '172.19.241.129',
        'ssh_port': 22,
        'ssh_user': 'root',
        'ssh_password': 'password'
    }
    mysql_config = {
        "host": "127.0.0.1",
        "port": None,
        "user": "root",
        "passwd": "root",
        "db": "pr_second",
        "charset": "utf8mb4",
    }
    tunnel = get_tunnel_ssh(ssh_config)
    mysql_config.update({"port": tunnel.local_bind_port})  # 注意mysql端口使用的是隧道的端口
    print(mysql_config)
    mysql_conn = pymysql.connect(**mysql_config)
    return mysql_conn


mysql_conn = get_mysql_conn()
cursor = mysql_conn.cursor()
cursor.execute("select * from pr_repo;")
data = cursor.fetchall()
print(data)
cursor.close()
mysql_conn.close()

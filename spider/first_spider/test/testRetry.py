import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time

access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
repo_name = "node"
# print(data)
i = 20000
while i < 40426:
    print("\n===一次哦===============" + str(i) + "====================================\n")
    # time.sleep(0.7)
    url = 'https://Google.com'
    # 调用api接口
    try:
        r = requests.get(url, headers=headers)
        print("url: " + url + "  Status Code:", r.status_code)
        i = i + 1
    except Exception as e:
        # 如果发生错误则回滚
        print("网络连接失败: ", url)
        filename = '_PR_network_exception.csv'
        write_file(i, repo_name, str(e) + url, filename)
        print(e)
        continue

    print(i)

import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
import traceback
import time

owner_name = "nodejs"
repo_name = "node"
index = 1
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
# 调用api接口
# 调用api接口
url = 'https://api.github.com/repos/' + owner_name + '/' + repo_name + '/pulls/' + index.__str__()
try:
    r = requests.get(url, headers=headers)
    print("url: " + url + "  Status Code:", r.status_code)
    index = index + 1
except Exception as e:
    # 如果发生错误则回滚
    print("网络连接失败: ", url)
    print(e)
    time.sleep(7)

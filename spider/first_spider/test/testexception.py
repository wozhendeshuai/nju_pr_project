import pymysql as db

import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file

owner_name = 'nodejs'
repo_name = 'node'
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}

'''
url = 'https://api.github.com/repos/' + +repo_name + '/pulls/3'
print(url)
r = requests.get(url, headers=headers)
print()
'''
for i in range(1, 20):
    # 调用api接口
    url = 'https://api.github.com/repos/' + owner_name + '/' + repo_name + '/pulls/' + i.__str__()
    print(url)
    r = requests.get(url, headers=headers)
    if r.status_code >= 300 or r.status_code < 200:
        write_file(i, repo_name, r.status_code.__str__() + str(r.json()))

'''
print("Status Code:", r.status_code)
print('status header', r.headers)
print(r.json())
json_str = r.json()
print(json_str)
print('r body: ', r.json()['body'])
print('json body: ', json_str['body'])
print('json created_at: ', time_reverse(json_str['created_at']))
'''

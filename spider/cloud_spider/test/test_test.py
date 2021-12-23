import time
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))
headers = {
    'Authorization': 'token '
}
index = 0
try:
    r = s.get('http://www.bhjy.net/', timeout=5, headers=headers)
    while (r.status_code >= 300 or r.status_code < 200):
        print(str(index) + "次访问，访问状态码：" + str(r.status_code))
        r = s.get('http://www.bhjy.net/', timeout=5, headers=headers)
        index = index + 1
        time.sleep(1)

except requests.exceptions.RequestException as e:
    print(e)

import time
import requests
from requests.adapters import HTTPAdapter

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))
headers = {
    'Authorization': 'token '
}
print(time.strftime('%Y-%m-%d %H:%M:%S'))
try:
    r = s.get('http://www.google.com.hk', timeout=5,headers=headers)
    print(r.text)
except requests.exceptions.RequestException as e:
    print(e)
print(time.strftime('%Y-%m-%d %H:%M:%S'))

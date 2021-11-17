import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
import traceback
import time
import json

# 计算一个字符串的单词数量(评论中的链接不算在内)
def wordCount(str) -> int:
    """
        计算某个字符串中单词数量，输入参数为字符串
        “Thanks! Should I create issue for this PR?\n”
        输出整型数字 8
        评论中的链接计算为一个单词
    """
    num = 0
    if str is None or str == '' or str == ' ' or len(str) == 0:
        num = 0
    else:
        num = len(str.strip().split(' '))
    return num


# 计算一个list中的单词数量
def wordCount_list(list):
    """
        计算一个字符串list中所有字符串的单词数量之和，输入参数为list
        ["Thanks! Should I create issue for this PR?\n","Up to you -- we've fixed it internally and will push it out to the git repo soon :).  Thanks for the typo fix!\n"]
        输出整型数字 33
        评论中的链接计算为一个单词
    """
    total = 0
    if len(list) == 0:
        return 0
    for str in list:
        if str is None or str == '' or str == ' ' or len(str) == 0:
            num = 0
        else:
            num = len(str.strip().split(' '))
        total += num
    return total


# 为了获得评论json中所有的body
def getBody(data):
    """
        将comments_content中的json中的多个body存储到一个list中
        输入参数为json语句
        [{"id": 155192251, "url": "https://api.github.com/repos/tensorflow/tensorflow/issues/comments/155192251",
        "body": "Hey webmaven: as mentioned in our [Contribution doc](https://github.com/tensorflow/tensorflow/blob/master/CONTRIBUTING.md), we don't accept pull requests through github yet.
        However, if you don't mind, I will make these edits internally and update the repository on our next upstream push with credit given to you.\n"}]
        输出body list
    """
    if len(data) == 0:
        return []
    for element in data:  # iterate on each element of the list
        # element is a dict
        body = element['body']  # get the body
        bodys = [e['body'] for e in data]
        return bodys


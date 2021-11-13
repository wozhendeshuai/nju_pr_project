import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
import traceback
import time
import json

# 判断is_contributor、is_core_member、is_reviewer
def is_text(author_association):
    """
        计算pr_user表中pr提交者和仓库的关系，是否为contributor、core_member、reviewer
        输入参数为json类型的author_association
        {"tensorflow": "CONTRIBUTOR"}
        输出为list，list[0]-list[2]分别对应变量is_contributor、is_core_member、is_reviewer
        变量值为0代表不是该关系，1代表是该关系
    """
    is_contributor = 0
    is_core_member = 0
    is_reviewer = 0
    if author_association is None:
        print("author_association为空")
    else:
        if author_association == "CONTRIBUTOR":
            is_contributor = 1
        elif author_association == "MEMBER":
            is_core_member = 1
        elif author_association == "REVIEWER":
            is_reviewer = 1
    is_list = []
    is_list.append(is_contributor)
    is_list.append(is_core_member)
    is_list.append(is_reviewer)
    return is_list


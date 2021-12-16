import pymysql as db
import requests
from utils.time_utils import time_reverse
from utils.access_token import get_token
from utils.exception_handdle import write_file
from requests.adapters import HTTPAdapter
import traceback
import time
import json

# 判断has_bug、has_document、has_feature、has_improve、has_refactor、Has_Test_Code、at_mention
def has_text(body):
    """
        计算pr的body中是否存在关键词bug、document、feature、improve、refactor、test、@
        输入参数为字符串body
        “Its JavaScript, google”
        输出为list，list[0]-list[6]分别对应变量has_bug、has_document、has_feature、has_improve、has_refactor、Has_Test_Code、at_mention
        变量值为0代表body中不存在该关键词，1代表存在
    """
    has_bug = 0
    has_document = 0
    has_feature = 0
    has_improve = 0
    has_refactor = 0
    Has_Test_Code = 0
    at_mention = 0
    if body is None:
        print("body为空")
    else:
        if "bug" in body:
            has_bug = 1
        if "document" in body:
            has_document = 1
        if "feature" in body:
            has_feature = 1
        if "improve" in body:
            has_improve = 1
        if "refactor" in body:
            has_refactor = 1
        if "test" in body:
            Has_Test_Code = 1
        if "@" in body:
            at_mention = 1
    list = []
    list.append(has_bug)
    list.append(has_document)
    list.append(has_feature)
    list.append(has_improve)
    list.append(has_refactor)
    list.append(Has_Test_Code)
    list.append(at_mention)
    return list

# 判断is_contributor、is_core_member、is_reviewer
def is_text(pr_author_association):
    """
        计算pr_self表中pr提交者和仓库的关系，是否为contributor、core_member、reviewer
        输入参数为字符串pr_author_association
        ”MEMBER“
        输出为list，list[0]-list[2]分别对应变量is_contributor、is_core_member、is_reviewer
        变量值为0代表不是该关系，1代表是该关系
    """
    is_contributor = 0
    is_core_member = 0
    is_reviewer = 0
    if pr_author_association is None:
        print("pr_author_association为空")
    else:
        if pr_author_association == "CONTRIBUTOR":
            is_contributor = 1
        elif pr_author_association == "MEMBER":
            is_core_member = 1
        elif pr_author_association == "REVIEWER":
            is_reviewer = 1
    print(pr_author_association)
    print(is_contributor)
    is_list = []
    is_list.append(is_contributor)
    is_list.append(is_core_member)
    is_list.append(is_reviewer)
    return is_list

# 判断is_responded，剔除自己review自己
def responded(num, review_comments_json, pr_user_id):
    """
        通过review_comments_content计算pr是否被响应，如果review_comments_content存在user且不为提交者自己，则被响应
        输入参数为整型的review计数器num，json类型的review_comments_json，整型的pr提交者的ID pr_user_id
        {
            {
            "user": {
                "login": "Yangqing",
                "id": 551151
                    }
            }
        }
        输出整型变量is_responded，0代表没有响应，1代表有响应
    """
    for i in range(0, len(review_comments_json)):
        if review_comments_json[i]["user"] is None:
            continue
        review_comments_content_id = review_comments_json[i]["user"]["id"]
        if review_comments_content_id != pr_user_id:
            num = num + 1
    if num > 0:
        is_responded = 1
    else:
        is_responded = 0
    return is_responded




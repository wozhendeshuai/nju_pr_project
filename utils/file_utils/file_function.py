from datetime import datetime
import dateutil
import json
from utils.time_utils import time_reverse


def get_file_type_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_file_dict:
       {
        733:  {
            file_name:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {'@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n     }'
            }
        }
       返回的dict为{id：涉及的文件类型数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        file_type_set = set()
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split = str(file_name_key).split('/')
            file_split = str(file_first_split[file_first_split.__len__() - 1]).split('.')
            file_type_set.add(file_split[file_split.__len__() - 1])

        re_dict[key] = file_type_set.__len__()
    return re_dict


def get_language_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_file_dict:
       {
        733:  {
            file_name:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {'@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n     }'
            }
        }
       返回的dict为{id：涉及的编程语言数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        language_type_set = set()
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split = str(file_name_key).split('/')
            file_split = str(file_first_split[file_first_split.__len__() - 1]).split('.')
            if file_split.__len__() > 1:
                language_type_set.add(file_split[file_split.__len__() - 1])

        re_dict[key] = language_type_set.__len__()
    return re_dict


def get_file_directory_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_file_dict:
       {
        733:  {
            file_name:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {'@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n     }'
            }
        }
       返回的dict为{id：涉及到的文件路径数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        directory_num = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split = str(file_name_key).split('/')
            directory_num = directory_num + file_first_split.__len__() - 1
        re_dict[key] = directory_num
    return re_dict


def get_segs_added_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：增加的代码段数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        temp_seg_add = 0
        temp_seg_delete = 0
        temp_seg_update = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split_arr = str(pr_file_dict[pr_number][file_name_key]).split('\\n')
            # print(file_first_split_arr)
            index = 0
            while index < file_first_split_arr.__len__():
                add_line = 0
                delete_line = 0
                if file_first_split_arr[index].__contains__("@@"):
                    index = index + 1
                    while index < file_first_split_arr.__len__():
                        temp_str = file_first_split_arr[index]
                        if temp_str[0] == '-':
                            delete_line = delete_line + 1
                        if temp_str[0] == '+':
                            add_line = add_line + 1
                        index = index + 1
                        if index < file_first_split_arr.__len__() and file_first_split_arr[index].__contains__("@@"):
                            break
                    if delete_line == 0 and add_line != 0:
                        temp_seg_add = temp_seg_add + 1
                else:
                    index = index + 1
        re_dict[key] = temp_seg_add
    return re_dict


def get_segs_deleted_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：删除的代码段数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        temp_seg_add = 0
        temp_seg_delete = 0
        temp_seg_update = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split_arr = str(pr_file_dict[pr_number][file_name_key]).split('\\n')
            # print(file_first_split_arr)
            index = 0
            while index < file_first_split_arr.__len__():
                add_line = 0
                delete_line = 0
                if file_first_split_arr[index].__contains__("@@"):
                    index = index + 1
                    while index < file_first_split_arr.__len__():
                        temp_str = file_first_split_arr[index]
                        if temp_str[0] == '-':
                            delete_line = delete_line + 1
                        if temp_str[0] == '+':
                            add_line = add_line + 1
                        index = index + 1
                        if index < file_first_split_arr.__len__() and file_first_split_arr[index].__contains__("@@"):
                            break
                    if add_line == 0 and delete_line != 0:
                        temp_seg_delete = temp_seg_delete + 1
                else:
                    index = index + 1
        re_dict[key] = temp_seg_delete
    return re_dict


def get_segs_updated_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：更新的代码段数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        temp_seg_add = 0
        temp_seg_delete = 0
        temp_seg_update = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            file_first_split_arr = str(pr_file_dict[pr_number][file_name_key]).split('\\n')
            # print(file_first_split_arr)
            index = 0
            while index < file_first_split_arr.__len__():
                add_line = 0
                delete_line = 0
                if file_first_split_arr[index].__contains__("@@"):
                    index = index + 1
                    while index < file_first_split_arr.__len__():
                        temp_str = file_first_split_arr[index]
                        if temp_str[0] == '-':
                            delete_line = delete_line + 1
                        if temp_str[0] == '+':
                            add_line = add_line + 1
                        index = index + 1
                        if index < file_first_split_arr.__len__() and file_first_split_arr[index].__contains__("@@"):
                            break
                    if add_line != 0 and delete_line != 0:
                        temp_seg_update = temp_seg_update + 1
                else:
                    index = index + 1
        re_dict[key] = temp_seg_update
    return re_dict


def get_test_inclusion(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：有测试文件为1，没有为0}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        has_test = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            file_name_split_arr = str(file_name_key).split('/')
            file_name = file_name_split_arr[file_name_split_arr.__len__() - 1].upper()
            if file_name.__contains__('TEST'):
                has_test = 1
                break
        re_dict[key] = has_test
    return re_dict


def get_subsystem_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：顶部路径代表子系统数量}
       """
    re_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        subsystem = set()
        for file_name_key in pr_file_dict[pr_number].keys():
            file_name_split_arr = str(file_name_key).split('/')
            if file_name_split_arr.__len__() == 0:
                continue
            subsystem.add(file_name_split_arr[0])

        re_dict[key] = subsystem.__len__()
    return re_dict


def get_changes_files_modified_num(pr_file_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：在本PR提交前，本PR涉及到的文件在之前被修改的数量}
       """
    re_dict = {}
    temp_pr_file_dict = {}
    for key in pr_file_dict.keys():
        pr_number = key
        pre_contain_pr_num = 0
        for file_name_key in pr_file_dict[pr_number].keys():
            if temp_pr_file_dict.__contains__(file_name_key):
                pre_contain_pr_num = pre_contain_pr_num + temp_pr_file_dict[file_name_key]
                temp_pr_file_dict[file_name_key] = temp_pr_file_dict[file_name_key] + 1
            else:
                temp_pr_file_dict[file_name_key] = 1

        re_dict[key] = pre_contain_pr_num
    return re_dict


def get_file_developer_num(pr_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：在本PR提交前，本PR涉及到的文件在之前被修改的数量}
       """
    re_dict = {}

    for key in pr_dict.keys():
        pr_number = key
        file_developer_set = set()
        commit_content = json.loads(pr_dict[pr_number])
        for i in range(len(commit_content)):
            if commit_content[i] is not None and commit_content[i]['author'] is not None:
                file_developer_set.add(commit_content[i]['author']['login'])

        re_dict[key] = file_developer_set.__len__()
    return re_dict


def get_file_developer_change_num(pr_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：在本PR提交前，本PR提交者提交的数量}
       """
    re_dict = {}
    file_developer_dict = {}
    for key in pr_dict.keys():
        pr_number = key
        commit_content = json.loads(pr_dict[pr_number])
        temp_developer_commit_num = 0
        for i in range(len(commit_content)):
            if commit_content[i] is not None and commit_content[i]['author'] is not None and \
                    commit_content[i]['author']['login'] is not None:
                if file_developer_dict.__contains__(commit_content[i]['author']['login']):
                    temp_developer_commit_num = file_developer_dict[commit_content[i]['author']['login']]
                    file_developer_dict[commit_content[i]['author']['login']] = file_developer_dict[
                                                                                    commit_content[i]['author'][
                                                                                        'login']] + 1

                elif commit_content[i]['author']['login'] is not None and file_developer_dict.__contains__(
                        commit_content[i]['author']['login']) is False:
                    file_developer_dict[commit_content[i]['author']['login']] = 1

        re_dict[key] = temp_developer_commit_num
    return re_dict


def get_file_developer_recent_change_num(pr_dict):
    """
        响应后到关闭时间的长度，对于还未close的pr不予计算
       获取pr中comments/review_comments中第一个非pr提交者评论时间，与pr关闭时间之差
       pr_dict:
       {
        733:  {
            'guacamole/src/main/java/org/apache/guacamole/rest/usergroup/UserGroupObjectTranslator.java': {
                '@@ -57,7 +57,7 @@ public void filterExternalObject(UserContext userContext, APIUserGroup object)\n             throws GuacamoleException {\n \n         // Filter object attributes by defined schema\n-        object.setAttributes(filterAttributes(userContext.getUserAttributes(),\n+        object.setAttributes(filterAttributes(userContext.getUserGroupAttributes(),\n                 object.getAttributes()));\n \n
                }'
            }
        }
       返回的dict为{id：在本PR提交前，本PR提交者提交的数量}
       """
    re_dict = {}
    file_developer_dict = {}
    pr_number_list = []
    for key in pr_dict.keys():
        pr_number_list.append(key)
    pr_number_list.sort()
    for index in range(pr_number_list.__len__()):
        pr_number = pr_number_list[index]
        outer_pr_created_time = pr_dict[pr_number]['created_at']
        outer_pr_commiter_and_time = get_user_and_submit_dict(pr_dict[pr_number]['commit_content'])
        day30_change = 0
        day60_change = 0
        day90_change = 0
        day120_change = 0
        for inner_index in range(index):
            inner_pr_commiter_and_time = get_user_and_submit_dict(pr_dict[pr_number_list[inner_index]]['commit_content'])
            for outer_commiter in outer_pr_commiter_and_time.keys():
                # 看看在之前的PR中是否有相同用户的提交
                if inner_pr_commiter_and_time.__contains__(outer_commiter) is False:
                    continue
                # 如果有相同的用户提交，则开始按照论文Early prediction of merged code changes to prioritize reviewing tasks 中的要求进行计算
                for inner_time in inner_pr_commiter_and_time.get(outer_commiter):
                    inner_time=time_reverse(inner_time)
                    if inner_time>outer_pr_created_time:
                        continue
                    else:
                        day=(outer_pr_created_time-inner_time).days
                        if day>=0 and day<=30:
                            day30_change=day30_change+1
                        elif day>30 and day<=60:
                            day60_change=day60_change+1
                        elif day > 60 and day <= 90:
                            day90_change = day90_change + 1
                        elif day > 90 and day <= 120:
                            day120_change = day120_change + 1
        re_dict[pr_number] = day30_change / 2 + day60_change / 3 + day90_change / 4 + day120_change / 5

    return re_dict


def get_user_and_submit_dict(commit_content):
    commit_content = json.loads(commit_content)
    re_dict = {}
    for i in range(len(commit_content)):
        if commit_content[i] is not None and commit_content[i]['author'] is not None and \
                commit_content[i]['author']['login'] is not None:
            if re_dict.__contains__(commit_content[i]['author']['login']):
                if commit_content[i]['commit']['author']['date'] < commit_content[i]['commit']['committer']['date']:
                    re_dict[commit_content[i]['author']['login']].append(
                        commit_content[i]['commit']['committer']['date'])
                else:
                    re_dict[commit_content[i]['author']['login']].append(commit_content[i]['commit']['author']['date'])

            elif commit_content[i]['author']['login'] is not None and re_dict.__contains__(
                    commit_content[i]['author']['login']) is False:
                if commit_content[i]['commit']['author']['date'] < commit_content[i]['commit']['committer']['date']:
                    re_dict[commit_content[i]['author']['login']] = [commit_content[i]['commit']['committer']['date']]
                else:
                    re_dict[commit_content[i]['author']['login']] = [commit_content[i]['commit']['author']['date']]

    return re_dict

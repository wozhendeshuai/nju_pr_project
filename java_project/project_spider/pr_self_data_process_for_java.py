import os
import sys
import time



if __name__ == '__main__':
    # print(os.path)
    path_temp = os.path.dirname(sys.path[0])
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 当前的环境为： ", path_temp)
    sys.path.append(path_temp)
    # print(path_temp)
    path_temp = os.path.dirname(path_temp)
    sys.path.append(path_temp)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " 当前的环境为： " + path_temp)

    from java_project.project_spider.spider_pr_self_for_java import get_pr_self_info

    from utils.access_token import get_token

    # 此部分可修改，用于控制进程
    index = 0
    max_pr_num = int(sys.argv[1])
    # helix-editor/helix
    owner_name = sys.argv[2]
    repo_name = sys.argv[3]
    # todo: 以后这里要从外界传入而非直接读文件
    access_token = get_token()

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
          " 当前的max_pr_num为： " + str(max_pr_num),
          " 当前的owner_name为： " + owner_name,
          " 当前的repo_name为： " + repo_name,
          " 当前的access_token为： " + access_token)

    headers = {
        'Authorization': 'token ' + access_token
    }

    get_pr_self_info(index, max_pr_num, owner_name, repo_name, headers)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
          owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
          owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
          owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")




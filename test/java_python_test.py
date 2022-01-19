import sys
import os
import time
if __name__ == '__main__':
    # print(os.path)
    path_temp = os.path.dirname(sys.path[0])
    sys.path.append(path_temp)
    # print(path_temp)
    path_temp = os.path.dirname(path_temp)
    sys.path.append(path_temp)
    # print(path_temp)
    # print(os.path.sys.path)

    # for i in range(sys.argv.__len__()):
    #     print(sys.argv[i])
    # if len(sys.argv) != 4:
    #     print("命令出错: python E:/pythonProject/nju_pr_project/test/java_python_test.py [参数1] [参数2] [参数3]")
    #     sys.exit(0)
    from utils.str_utils.str_function import wordCount

    print(sys.argv[1])
    print(sys.argv[2])
    maxPRNum=sys.argv[1]
    ownerName=sys.argv[2]
    repoName=sys.argv[3]
    for i in range(sys.argv.__len__()):
        print(maxPRNum,ownerName,repoName,i)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        time.sleep((i+1)*2)
    print(sys.argv[1])
    # print(wordCount(sys.argv[1]))
    # print(sys.argv[2])
    # print(sys.argv[3])

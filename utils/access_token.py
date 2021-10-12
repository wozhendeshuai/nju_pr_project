# 获取本地文件中的access_tocken相关值
def get_token():
    file = open('E:\\pythonProject\\nju_pr_project\\utils\\access_token.txt', 'r')
    str = file.readline()
    # print(str)
    file.close()
    return str
# get_token()

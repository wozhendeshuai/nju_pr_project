# 获取本地文件中的access_tocken相关值
def get_token(num=0):
    file = open('E:\\pythonProject\\nju_pr_project\\utils\\access_token.txt', 'r')
    list = file.readlines()
    lines = len(list)
    # str = file.readline()
    print(lines)
    str = list[num % lines]
    file.close()
    str = str.replace("\n", "")
    print(str)
    return str
# get_token()

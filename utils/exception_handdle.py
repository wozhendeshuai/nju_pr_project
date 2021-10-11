# 处理无法获得的PR，然后记录到文件中，记录格式如下，时间|PRNumber，时间|PR编号
import os
import time


def write_file(pr_number, project_name, exception):
    current_path = os.getcwd()  # 获取当前路径
    print(current_path)
    filename = project_name + '_exception_PRNumbers.csv'
    path = current_path + '\\' + filename  # 在当前路径创建名为test的文本文件
    now_time = time.strftime('%Y-%m-%d %H:%M:%S ', time.localtime(time.time()))  # 获取当前时间
    context = project_name + "," + pr_number.__str__() + ',' + now_time + ',' + exception + "\n"
    print(path)
    if os.path.exists(path):
        print(path + ' is already exist')
        print('context is :' + context)
        file = open(path, 'a+')
        file.write(context)
        file.close()
    else:
        file = open(path, 'a+')
        file.write(context)
        file.close()


write_file(100, 'jsonjson', "404")

print("当前时间： ", time.strftime('%Y-%m-%d %H:%M:%S ', time.localtime(time.time())))

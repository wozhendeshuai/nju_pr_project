import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

nat = np.datetime64('NaT')


def nat_check(nat):
    return nat == np.datetime64('NaT')


def distance(vecA, vecB):
    '''
    计算两个向量之间欧氏距离的平方
    :param vecA: 向量A的坐标
    :param vecB: 向量B的坐标
    :return: 返回两个向量之间欧氏距离的平方
    '''
    dist = (vecA - vecB) * (vecA - vecB).T
    return dist[0, 0]


def randomCenter(data, k):
    '''
    随机初始化聚类中心
    :param data: 训练数据
    :param k: 聚类中心的个数
    :return: 返回初始化的聚类中心
    '''
    n = np.shape(data)[1]  # 特征的个数
    cent = np.mat(np.zeros((k, n)))  # 初始化K个聚类中心
    for j in range(n):  # 初始化聚类中心每一维的坐标
        minJ = np.min(data[:, j])
        rangeJ = np.max(data[:, j]) - minJ
        cent[:, j] = minJ * np.mat(np.ones((k, 1))) + np.random.rand(k, 1) * rangeJ  # 在最大值和最小值之间初始化
    return cent


def kmeans(data, k, cent):
    '''
    kmeans算法求解聚类中心
    :param data: 训练数据
    :param k: 聚类中心的个数
    :param cent: 随机初始化的聚类中心
    :return: 返回训练完成的聚类中心和每个样本所属的类别
    '''
    m, n = np.shape(data)  # m：样本的个数；n：特征的维度
    subCenter = np.mat(np.zeros((m, 2)))  # 初始化每个样本所属的类别
    change = True  # 判断是否需要重新计算聚类中心
    while change == True:
        change = False  # 重置
        for i in range(m):
            minDist = np.inf  # 设置样本与聚类中心的最小距离，初始值为正无穷
            minIndex = 0  # 所属的类别
            for j in range(k):
                # 计算i和每个聚类中心的距离
                dist = distance(data[i,], cent[j,])
                if dist < minDist:
                    minDist = dist
                    minIndex = j
            # 判断是否需要改变
            if subCenter[i, 0] != minIndex:  # 需要改变
                change = True
                subCenter[i,] = np.mat([minIndex, minDist])
        # 重新计算聚类中心
        for j in range(k):
            sum_all = np.mat(np.zeros((1, n)))
            r = 0  # 每个类别中样本的个数
            for i in range(m):
                if subCenter[i, 0] == j:  # 计算第j个类别
                    sum_all += data[i,]
                    r += 1
            for z in range(n):
                try:
                    cent[j, z] = sum_all[0, z] / r
                except:
                    print("ZeroDivisionError: division by zero")
    return subCenter, cent


def load_data(file_path):
    '''
    导入数据
    :param file_path: 文件路径
    :return: 以矩阵的形式返回导入的数据
     # io 表示excel文件路径
    # sheet_index 表示读取第几个sheet，sheet_name可指定名称，默认0
    # header 表示表头最后是第几行，读取数据掠过表头数据用，默认为0第一行掠过去
    '''
    data = pd.read_excel(io=file_path)
    print(len(data))
    return_data = []
    for line in data.index:
        print(line)
    for i in data.index.values:  # 获取行号的索引，并对其进行遍历：
        # 根据i来获取每一行指定的数据 并利用to_dict转成字典
        row_data = data.loc[i, ['pr_number', 'created_at', 'updated_at', 'close_at']].to_dict()
        if pd.isna(row_data['close_at']) or pd.isna('updated_at') or pd.isna('created_at'):
            pd.isnull
            continue
            # created_at转为时间戳
        created_time = row_data['created_at']
        created_timestamp = time.mktime(created_time.timetuple())
        # print("created_time", created_time)
        # print("created_timestamp", created_timestamp)

        # updated_at转为时间戳
        updated_at_time = row_data['updated_at']
        updated_at_timestamp = time.mktime(updated_at_time.timetuple())
        # print("updated_at_time", updated_at_time)
        # print("updated_at_timestamp", updated_at_timestamp)

        # close_at转为时间戳
        close_at_time = row_data['close_at']
        close_at_timestamp = time.mktime(close_at_time.timetuple())
        # print("close_at_time", close_at_time)
        # print("close_at_timestamp", close_at_timestamp)
        #
        # print(updated_at_timestamp - created_timestamp)
        #
        # print(close_at_timestamp - created_timestamp)
        row = []  # 记录每一行
        row.append(float(updated_at_timestamp - created_timestamp))  # 将文本中的特征转换成浮点数
        row.append(float(close_at_timestamp - created_timestamp))
        return_data.append(row)
    return np.mat(return_data)  # 以矩阵的形式返回


def save_result(file_name, data):
    '''
    保存source中的结果到file_name文件中
    :param file_name: 保存的文件名
    :param data: 需要保存的数据
    :return:
    '''
    m, n = np.shape(data)
    f = open(file_name, "w")
    for i in range(m):
        tmp = []
        for j in range(n):
            tmp.append(str(data[i, j]))
        f.write("\t".join(tmp) + "\n")
    f.close()

def plot_show(data_temp,Muk):
    data=data_temp.A
    typen1_x=[]
    typen1_y=[]
    for i in range(len(data)):
        typen1_x.append(data[i][0])
        typen1_y.append(data[i][1])
    fig = plt.figure()
    axes = fig.add_subplot(111)
    typen1 = axes.scatter(typen1_x, typen1_y, c='r', marker='o')
    plt.xlabel('x')
    plt.ylabel('y')
    # 画聚类中心
    Muk=Muk.A
    plt.scatter(Muk[:, 0], Muk[:, 1], marker='*', s=60)
    for i in range(k):
        plt.annotate('中心' + str(i + 1), (Muk[i, 0], Muk[i, 1]))
    plt.show()
   # axes.legend((typep1, typen1), ('positive', 'negative'))
    plt.show()

if __name__ == "__main__":
    k = 100  # 聚类中心的个数

    file_path = "C:\\Users\\junyujia\\Desktop\\ipython_pr_test.xlsx"
    print("file_path", file_path)
    tempdata=load_data(file_path)

    subCenter, center = kmeans(load_data(file_path), k, randomCenter(load_data(file_path), k))
    plot_show(tempdata,center)
    save_result("E:\\pythonProject\\nju_pr_project\\data_process\\kmeans_sub", subCenter)
    save_result("E:\\pythonProject\\nju_pr_project\\data_process\\kmeans_center", center)

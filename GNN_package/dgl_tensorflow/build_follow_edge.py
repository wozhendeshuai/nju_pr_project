from numpy.lib.function_base import append, i0, percentile
from pymysql import NULL
import getData
import numpy as np
import dgl
import dgl.nn as dglnn
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from dgl.data.utils import generate_mask_tensor
from dgl.data import DGLDataset
import torch
from sklearn.metrics import hamming_loss
import json
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#从数据库获取user信息
raw_data=getData.getDataFromSql(
    "select user_id,followers,following from pr_user"
)

dict_follower=[]
dict_following=[]
for item in raw_data:
    ##follower
    tmp=[]
    for i in eval(item[1]).split(';'):
        id=i.split('-')[0]
        if id!='':
            tmp.append(int(id))
    dict_follower.append((item[0],tmp))
    ##following
    tmp=[]
    for i in eval(item[2]).split(';'):
        id=i.split('-')[0]
        if id!='':
            tmp.append(int(id))
    dict_following.append((item[0],tmp))

##user的follower和following
dict_follower=dict(dict_follower)
dict_following=dict(dict_following)

user_path_data=getData.getDataFromSql(
    "select pr_user_id from pr_self"
)

##打pr_id
process_data=[]
count=0
for item in user_path_data:
    process_data.append([item[0],count])
    count+=1

f1 = open(basedir+"/edge_follow_source.txt",'w')
f2 = open(basedir+"/edge_follow_destination.txt",'w')

print("processing...")

##构边并保存
for item in process_data:
    if item[0] in dict_follower.keys():
        for i in dict_follower[item[0]]:
            for j in process_data:
                if i==j[0]:
                    f1.writelines(str(item[1])+'\n')
                    f2.writelines(str(j[1])+'\n')
        
        for i in dict_following[item[0]]:
            for j in process_data:
                if i==j[0]:
                    f1.writelines(str(item[1])+'\n')
                    f2.writelines(str(j[1])+'\n')

f1.close()
f2.close()
print("done!")






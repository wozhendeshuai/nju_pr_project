
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

user_data=getData.getDataFromSql(
    "select user_id,user_following,user_followers from pr_user"
)

dict_user_following=[]
dict_user_follower=[]
for i in user_data:
    tmp_following=[]
    tmp_follower=[]
    for j in i[1].split(';'):
        id=j.split('-')[0]
        if id!='':
            id=int(id)
            tmp_following.append(id)
    for j in i[2].split(';'):
        id=j.split('-')[0]
        if id!='':
            id=int(id)
            tmp_follower.append(id)

    dict_user_following.append((i[0],tmp_following))
    dict_user_follower.append((i[0],tmp_follower))

dict_user_following=dict(dict_user_following)
dict_user_follower=dict(dict_user_follower)

count=0
e_follow=[]     ##互为追随者                                               
for i in dict_user_following.items():
    tmp=[]
    for j in i[1]:
        if j in dict_user_follower[i[0]]:
            tmp.append(j)
    if len(tmp)!=0:    
        e_follow.append((i[0],tmp))

e_follow=dict(e_follow)
print(len(e_follow))
print(len(e_follow.keys()))
print(count)
# print(e_follow)

# count=0
# for i in e_follow.values():
#     count+=1
# print(count)

# for i in e_follow.keys():
#     print(e_follow[i])

from types import prepare_class
import torch

import numpy as np
import torch.nn as nn
import torch.optim as optim
from GraphSage import GraphSage
from data import GraphData_train
from sample import multihop_sampling
from sklearn.metrics import hamming_loss


from collections import namedtuple

# 5.2 数据准备

data = GraphData_train().data
x=data.x
# x = data.x / data.x.sum(1, keepdims=True)  # 归一化数据，使得每一行和为1

train_index = np.where(data.train_mask)[0]
# train_label = data.y[train_index]
test_index = np.where(data.test_mask)[0]

label=[]
y=np.sort(data.y,axis=0)

# 求五等分点
l=y.shape[0]
idx=[int(l/5),int(l*2/5),int(l*3/5),int(l*4/5)]
threshold=[]
for i in idx:
    threshold.append(y[i])

# 根据响应速度打标签 1,2,3,4,5
for i in data.y:
    tmp=[]
    for j in i:
        if j<threshold[0]:
            tmp.append(5)
        elif j<threshold[1]:
            tmp.append(4)
        elif j<threshold[2]:
            tmp.append(3)
        elif j<threshold[3]:
            tmp.append(2)
        else:
            tmp.append(1)
    label.append(tmp)

label=np.array(label)

train_label = label[train_index]


#   输出：  
# Node's feature shape:  (2708, 1433)
# Node's label shape:  (2708,)
# Adjacency's shape:  2708
# Number of training nodes:  140
# Number of validation nodes:  500
# Number of test nodes:  1000
#   可以看到，数据集中共有2708个节点，节点特征有1433维，因此，GraphSAGE的输入维度INPUT_DIM = 1433。  
# 5.3 模型初始化
 
INPUT_DIM = 44    # 输入维度
# Note: 采样的邻居阶数需要与GCN的层数保持一致
HIDDEN_DIM = [100, 1]   # 隐藏单元节点数
NUM_NEIGHBORS_LIST = [10, 10]   # 每阶采样邻居的节点数
assert len(HIDDEN_DIM) == len(NUM_NEIGHBORS_LIST)
BTACH_SIZE = 50     # 批处理大小
EPOCHS = 1
NUM_BATCH_PER_EPOCH = int(train_index.shape[0]/BTACH_SIZE)+1    # 每个epoch循环的批次数
LEARNING_RATE = 0.01    # 学习率
NUM_BATCH_PER_EPOCH_TEST=int(test_index.shape[0]/BTACH_SIZE)+1
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = GraphSage(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM,
                  num_neighbors_list=NUM_NEIGHBORS_LIST).to(DEVICE)
print(model)


# criterion = nn.BCELoss().to(DEVICE)
criterion=nn.MSELoss(reduction='mean').to(DEVICE)

optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=5e-4)

import torch.nn.functional as F
def listnet_loss(y_i, z_i):
    """
    y_i: (n_i, 1) 维度
    z_i: (n_i, 1)
    """

    P_y_i = F.softmax(y_i, dim=0)
    P_z_i = F.softmax(z_i, dim=0)
    # print(torch.log(P_z_i))
    # print(y_i)
    # print(z_i)
    return - torch.sum(P_y_i * torch.log(P_z_i))

def train():
    model.train()
    for e in range(EPOCHS):
        for batch in range(NUM_BATCH_PER_EPOCH):

            start=batch*BTACH_SIZE
            end=start+BTACH_SIZE
            if end>train_index.shape[0]:
                end=train_index.shape[0]
            batch_src_index=train_index[start:end]
            batch_src_label = torch.from_numpy(train_label[batch_src_index]).float().to(DEVICE)
            batch_sampling_result = multihop_sampling(batch_src_index, NUM_NEIGHBORS_LIST, data.adjacency_dict)        
            batch_sampling_x = [torch.from_numpy(x[idx]).float().to(DEVICE) for idx in batch_sampling_result]
            
            batch_train_logits = model(batch_sampling_x)            
            optimizer.zero_grad()

            # loss=criterion(batch_train_logits,batch_src_label)  

            loss=listnet_loss(batch_src_label,batch_train_logits)       
            
            loss.backward(retain_graph=True)  # 反向传播计算参数的梯度
            optimizer.step()  # 使用优化方法进行梯度更新
            # print("Epoch {:03d} Batch {:03d} Loss: {:.4f}".format(e, batch, loss.item()))
            torch.save(model.state_dict(), 'logs')
        evaluate()

def evaluate():
    
    model.eval()
    with torch.no_grad():
        L=[]
        for batch in range(NUM_BATCH_PER_EPOCH_TEST):
            start=batch*BTACH_SIZE
            end=start+BTACH_SIZE
            if end>test_index.shape[0]:
                end=test_index.shape[0]
            batch_src_index=test_index[start:end]
            # batch_src_index=train_index[start:end]
            
            batch_src_label = torch.from_numpy(label[batch_src_index]).float().to(DEVICE)
            batch_sampling_result = multihop_sampling(batch_src_index, NUM_NEIGHBORS_LIST, data.adjacency_dict)
            batch_sampling_x = [torch.from_numpy(x[idx]).float().to(DEVICE) for idx in batch_sampling_result]
            
            batch_train_logits = model(batch_sampling_x)

            # 求ndcg
            dict_ground_truth=dict()

            batch_src_label=batch_src_label.cpu().numpy()
            for i,id in enumerate(batch_src_index):
                dict_ground_truth[id]=batch_src_label[i]
            
            groud=[]
            for i in batch_src_label:
                groud.append(i[0])
            groud.sort(reverse=True)

                        
            dict_pred=dict()
            for i,id in enumerate(batch_src_index):
                dict_pred[id]=batch_train_logits[i]
            
            dict_pred_ranking=[]
            for id in sorted(dict_pred.items(), key=lambda item:item[1], reverse=True):
                dict_pred_ranking.append(id[0])
                        
            pred_in_true_list=[]
            for i in dict_pred_ranking:
                pred_in_true_list.append(dict_ground_truth[i][0])
                    
            p=end-start
            discount=1/(np.log2(np.arange(p)+2))
            
            
            rel_true = np.array(groud)
            # groud.sort()
            # rel_pred=np.array(groud)
            rel_pred=np.array(pred_in_true_list)

            
            # print(rel_pred)


            idcg=np.sum(rel_true[:p]*discount)
            dcg=np.sum(rel_pred[:p]*discount)
            loss=dcg/idcg
            L.append(loss)        
        
        sum=0
        for item in L:
            sum+=item
        ndcg=sum/len(L)
        print("Test Accuracy: ", ndcg)



train()
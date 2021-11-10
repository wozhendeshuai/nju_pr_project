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


###is_merged,0-》reject
###1的话看first_comment_member_id==pr_user_id或者为空 accept
###剩下的response


###状态不全，reopen

###costsensitive 人力资源，情感资源

##从数据库获取数据
raw_data=getData.getDataFromSql(
    "select pr_file_edit_num\
    ,pr_line_add_num,pr_line_del_num,commits_num\
    ,mergeable,comments_number\
    ,is_merged,pr_user_id\
    ,first_comment_member_id from tensorflow_pr_test"
)

###数据有问题，有的comments_number=0，却有first_comment_member_id
###有的first_comment_member_id==NULL，comments_number却不为0

###统计accept数量
s=0
count=0
total=0
for i in raw_data:
    total+=1
    if i[6]==1:
        if i[8]==None or i[7]==i[8] and i[5]<=1:
            count+=1
s+=count
print("accept占比："+str(count/total))

###统计response数量
count=0
total=0
for i in raw_data:
    total+=1
    if i[6]==1:
        if i[8]!=None and (i[7]!=i[8] or i[5]>1):
            count+=1
s+=count
print("response占比："+str(count/total))


###统计reject数量
count=0
total=0
for i in raw_data:
    total+=1
    if i[6]==0:
        count+=1
s+=count
print("reject占比："+str(count/total))

print(total)
print(s)

##tuple->List
##[pr_file_edit_num,pr_line_add_num,pr_line_del_num,
# commits_num,mergeable,comments_number,is_merged,pr_user_id,
# first_comment_member_id,pr_id,Y_label]
data=[]
count=0
for item in raw_data:
    tmp=[]
    for i in item:
        tmp.append(i)
    tmp.append(count)
    if item[6]==0:
        tmp.append(2)
    else:
        if item[8]==None or item[7]==item[8] and item[5]<=1:
            tmp.append(0)
        else:
            tmp.append(1)
    count+=1
    data.append(tmp)


X=[]
edge_source=[]
edge_target=[]
Y=[] ###0-accept 1-response 2-reject


for i in data:
    X.append([i[0],i[1],i[2],i[3],i[4],i[5]])
    Y.append(i[10]) 


###归一化
X=np.array(X)
mins = X.min(0) #返回data矩阵中每一列中最小的元素，返回一个列表
maxs = X.max(0) #返回data矩阵中每一列中最大的元素，返回一个列表
ranges = maxs - mins #最大值列表 - 最小值列表 = 差值列表
normData = np.zeros(np.shape(X)) #生成一个与 data矩阵同规格的normData全0矩阵，用于装归一化后的数据
row = X.shape[0] #返回 data矩阵的行数
normData = X - np.tile(mins,(row,1)) #data矩阵每一列数据都减去每一列的最小值
normData = normData / np.tile(ranges,(row,1))
X=normData.tolist()
print(len(X))
print(len(Y))

for i in data:
    for j in data:
        if i[9]<j[9] and i[7]==j[7]:
            edge_source.append(i[9])
            edge_target.append(j[9])

print(len(edge_target))


user_data=getData.getDataFromSql(
    "select user_id,user_following,user_followers from pr_user_1"
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


e_follow=[]     ##互为追随者                                               
for i in dict_user_following.items():
    tmp=[]
    for j in i[1]:
        if j in dict_user_follower[i[0]]:
            tmp.append(j)
    if len(tmp)!=0:    
        e_follow.append((i[0],tmp))

e_follow=dict(e_follow)

for i in data:
    if i[7] in e_follow.keys():
        for j in data:
            if j[7] in e_follow[i[7]]:
                edge_source.append(i[9])
                edge_target.append(j[9])

print(len(edge_target))


def build_karate_club_graph():
    
    src = np.array(edge_source)
    dst = np.array(edge_target)
    # Edges are directional in DGL; Make them bi-directional.
    u = np.concatenate([src, dst])
    v = np.concatenate([dst, src])
    # Construct a DGLGraph
    return dgl.graph((u, v))

G = build_karate_club_graph()


print(G.number_of_nodes())
idx_train = np.array(range(int(G.number_of_nodes() * 0.6)))
idx_val = idx_train + int(G.number_of_nodes() * 0.2)
idx_test = np.array([i for i in np.array(range(G.number_of_nodes())) if (i not in idx_train) and (i not in idx_val)])
labels = torch.tensor(Y, dtype=torch.long)

def _sample_mask(idx, l):
    """Create mask."""
    mask = np.zeros(l)
    mask[idx] = 1
    return mask

class MyDataset(DGLDataset):
    def __init__(self,
                 url=None,
                 raw_dir=None,
                 save_dir=None,
                 force_reload=False,
                 verbose=False):
        super(MyDataset, self).__init__(name='dataset_name',
                                        url=url,
                                        raw_dir=raw_dir,
                                        save_dir=save_dir,
                                        force_reload=force_reload,
                                        verbose=verbose)

    def process(self):
        # 跳过一些处理的代码
        # === 跳过数据处理 ===

        # 构建图
        # g = dgl.graph(G)
        g = G

        train_mask = _sample_mask(idx_train, g.number_of_nodes())
        val_mask = _sample_mask(idx_val, g.number_of_nodes())
        test_mask = _sample_mask(idx_test, g.number_of_nodes())

        # 划分掩码
        g.ndata['train_mask'] = generate_mask_tensor(train_mask)
        g.ndata['val_mask'] = generate_mask_tensor(val_mask)
        g.ndata['test_mask'] = generate_mask_tensor(test_mask)

        # 节点的标签
        g.ndata['label'] = labels.clone().detach()
        # 节点的特征
        g.ndata['feat'] = torch.tensor(X, dtype=torch.float)
        self._num_labels = int(torch.max(labels).item() + 1)
        self._labels = labels
        self._g = g

    def __getitem__(self, idx):
        assert idx == 0, "这个数据集里只有一个图"
        return self._g

    def __len__(self):
        return 1


class SAGE(nn.Module):
    def __init__(self, in_feats, hid_feats, out_feats):
        super().__init__()
        # 实例化SAGEConve，in_feats是输入特征的维度，out_feats是输出特征的维度，aggregator_type是聚合函数的类型
        self.conv1 = dglnn.SAGEConv(
            in_feats=in_feats, out_feats=hid_feats, aggregator_type='pool')
        self.conv2 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=hid_feats, aggregator_type='pool')
        self.conv3 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=out_feats, aggregator_type='pool')

    def forward(self, graph, inputs):
        # 输入是节点的特征
        h = self.conv1(graph, inputs)
        h = F.relu(h)
        h = self.conv2(graph, h)
        h = F.relu(h)
        h = self.conv3(graph, h)
        h = F.log_softmax(h,dim=1)
        return h

dataset = MyDataset()
# dataset = dgl.data.CiteseerGraphDataset()

graph = dataset[0]
node_features = graph.ndata['feat']
node_labels = graph.ndata['label']
train_mask = graph.ndata['train_mask']
valid_mask = graph.ndata['val_mask']
test_mask = graph.ndata['test_mask']
n_features = node_features.shape[1]
n_labels = int(node_labels.max().item() + 1)

def evaluate(model, graph, features, labels, mask):
    model.eval()
    with torch.no_grad():
        logits = model(graph, features)
        logits = logits[mask]
        labels = labels[mask]
        _, indices = torch.max(logits, dim=1)
        correct = torch.sum(indices == labels)
        return correct.item() * 1.0 / len(labels)

model = SAGE(in_feats=n_features, hid_feats=100, out_feats=n_labels)
opt = torch.optim.Adam(model.parameters())

for epoch in range(20): 
    model.train()
    # 使用所有节点(全图)进行前向传播计算
    logits = model(graph, node_features)
    # print(logits)
    # 计算损失值
    loss = F.nll_loss(logits[train_mask], node_labels[train_mask])
    # 计算验证集的准确度
    acc = evaluate(model, graph, node_features, node_labels, valid_mask)
    # 进行反向传播计算
    opt.zero_grad()
    loss.backward()
    opt.step()
    print("epoch"+str(epoch))
    print("loss:"+str(loss.item()))
    print("acc:"+str(acc))
    print("--------")
    Acc=evaluate(model, graph, node_features, node_labels, test_mask)
    print(Acc)    




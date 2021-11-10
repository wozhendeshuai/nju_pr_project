##从username获取他们拥有的仓库
import pymysql
import numpy as np
from torch._C import AggregationType

##连接数据库
conn=pymysql.connect(
    host="127.0.0.1",
    port=3306,#端口号
    user="root",#数据库用户
    password="123456",#数据库密码
    database="spider"#要连接的数据库名称
)

cursor=conn.cursor()#游标


###从username数据库获取所有的name
sql="select is_merged,comments_number,pr_file_edit_num\
    ,pr_line_add_num,pr_line_del_num,commits_num\
        ,created_at,close_at,pr_user_id,pr_number from puppet_pr_test"
cursor.execute(sql)
data=cursor.fetchall()
# print(len(data))

filter_data=[]

for i in data:
    if i[6]==None or i[7]==None:
        continue
    else:
        filter_data.append(i)


# print(filter_data)

duration=[]
for i in filter_data:
    duration.append([(i[7]-i[6]).total_seconds()/60,(i[7]-i[6]).total_seconds()/60])

# print(len(duration))

duration=np.array(duration)


import numpy as np 
from sklearn.cluster import KMeans 
from scipy.spatial.distance import cdist 
import matplotlib.pyplot as plt

X=duration

kmeans = KMeans(n_clusters=7)
kmeans.fit(X)
Y=kmeans.fit_predict(X)

count=0
K=[0,1,2,3,4,5,6]
# for i in K:
#     count=0
#     for j in Y:
#         if(j==i):
#             count+=1
    # print(count)

edge_source=[]
edge_target=[]

Tmp=[]
count=0
for i in filter_data:
    Tmp.append([i[8],count])
    count+=1

for i in Tmp:
    for j in Tmp:
        if i[1]<=j[1] and i[0]==j[0]:
            edge_source.append(i[1])
            edge_target.append(j[1])


print(len(edge_source))
print(len(edge_target))

X=[]

for i in filter_data:
    X.append([i[0],i[1],i[2],i[3],i[4],i[5]])
print(len(X))
print(len(Y))
print(max(edge_target))


import dgl
import dgl.nn as dglnn
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from dgl.data.utils import generate_mask_tensor
from dgl.data import DGLDataset
import torch

def build_karate_club_graph():
    # All 78 edges are stored in two numpy arrays. One for source endpoints
    # while the other for destination endpoints.
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
            in_feats=in_feats, out_feats=hid_feats, aggregator_type='gcn')
        self.conv2 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=hid_feats, aggregator_type='gcn')
        self.conv3 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=hid_feats, aggregator_type='gcn')
        self.conv4 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=hid_feats, aggregator_type='gcn')
        self.conv5 = dglnn.SAGEConv(
            in_feats=hid_feats, out_feats=out_feats, aggregator_type='gcn')

    def forward(self, graph, inputs):
        # 输入是节点的特征
        h = self.conv1(graph, inputs)
        h = F.relu(h)
        h = self.conv2(graph, h)
        h = F.relu(h)
        h = self.conv3(graph, h)
        h = F.relu(h)
        h = self.conv4(graph, h)
        h = F.relu(h)
        h = self.conv5(graph, h)
        h = F.log_softmax(h)
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

model = SAGE(in_feats=n_features, hid_feats=50, out_feats=n_labels)
opt = torch.optim.Adam(model.parameters())

for epoch in range(50): 
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
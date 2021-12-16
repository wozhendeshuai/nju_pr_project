import torch
from torch_geometric.data import Data

import networkx as nx
import matplotlib.pyplot as plt
from pyg2plot import Plot

def draw(edge_index, name=None):
    G = nx.Graph(node_size=15, font_size=8)
    src = edge_index[0].cpu().numpy()
    dst = edge_index[1].cpu().numpy()
    edgelist = zip(src, dst)
    for i, j in edgelist:
        G.add_edge(i, j)
    for  i in src:
        G.add_node(i)
    plt.figure(figsize=(20, 14))  # 设置画布的大小
    nx.draw_networkx(G,with_labels=True)
    plt.show()
    #plt.savefig('{}.png'.format(name if name else 'path'))

edge_index = torch.tensor([[0, 1, 1, 2],
                            [1, 0, 2, 1]], dtype=torch.long)
x = torch.tensor([[-1], [0], [1]], dtype=torch.float)
data = Data(x=x, edge_index=edge_index)
print(data)
draw(edge_index, 'TEST')

edge_index2 = torch.tensor([[0,1],[1,0],[1,2],[2,1]],dtype=torch.long)
x2=torch.tensor([[-1],[0],[1]],dtype=torch.float)
data2=Data(x2,edge_index2)
print(data2)

print(data.keys)
print(data['x'])
for key,item in data:
    print("{} found in data".format(key))
print("num_nodes",data.num_nodes)
print("num_edges",data.num_edges)
print("num_faces",data.num_faces)
print("num_features",data.num_features)
print("num_edge_features",data.num_edge_features)
print("num_node_features",data.num_node_features)
#用GPU呢
device=torch.device('cuda')
data=data.to(device)
print(data)
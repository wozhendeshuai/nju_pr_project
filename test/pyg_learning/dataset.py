from torch_geometric.datasets import TUDataset,Planetoid
# dataset=TUDataset(root='/tmp/ENZYMES',name='ENZYMES')
# print(len(dataset))
# print(dataset.num_classes)
# print(dataset.num_node_features)
# data=dataset[0]
# print(data.is_undirected())
# dataset=dataset.shuffle()
dataset2=Planetoid('/tmp/Cora',name='Cora')
print(len(dataset2))
print(dataset2.num_classes)
print(dataset2.num_node_features)
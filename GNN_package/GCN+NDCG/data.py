import os.path as osp
from collections import namedtuple
import numpy as np
import pandas as pd
import torch


Data = namedtuple('Data', ['x', 'y', 'adjacency_dict',
                           'train_mask', 'test_mask'])

class GraphData_train(object):
    

    def __init__(self, data_root="./"):
        """
        数据可以通过属性 .data 获得，它将返回一个数据对象，包括如下几部分：
            * x: 节点的特征，维度为 15462 * 44，类型为 np.ndarray
            * y: 节点的标签，总共包括2个属性，类型为 np.ndarray
            * adjacency_dict: 邻接信息，，类型为 dict
            * train_mask: 训练集掩码向量，当节点属于训练集时，相应位置为True，否则False
            * test_mask: 测试集掩码向量，当节点属于测试集时，相应位置为True，否则False
        Args:
        -------
            data_root: string, optional
                存放数据的目录，原始数据路径: {data_root}/raw
                缓存数据路径: {data_root}/processed_cora.pkl
        """
     
        self.node_path=osp.join(data_root, "nodes_data_spring-boot.csv")
        self.edge_path=osp.join(data_root, "edges_data_spring-boot.csv")
      
        self._data = self.process_data()
         



    def process_data(self):
        """
        处理数据，得到节点特征和标签，邻接矩阵，训练集、验证集以及测试集
        """
        print("Process data ...")
    
        nodes_data = pd.read_csv(self.node_path)
        edges_data = pd.read_csv(self.edge_path)

        # 取前80%的PR作为训练集
        nodes_data=nodes_data[:int(len(nodes_data)*0.8)]
        edges_data=edges_data.loc[edges_data['SrcId']<len(nodes_data)]
        edges_data=edges_data.loc[edges_data['DesId']<len(nodes_data)]


        ##节点特征
        x = nodes_data[['author_identity',
                        'has_labels',
                        'mergable_state',
                        'has_assignees_content',
                        'comment_num',
                        'review_comment_num',
                        'commit_num',
                        'file_changed_num',
                        'total_add_line',
                        'total_delete_line',
                        'self_accept_rate',
                        'self_closed_num_rate',
                        'self_contribution_rate',
                        'project_accept_rate',
                        'is_weekday',
                        'label_count',
                        'workload',
                        'pre_prs',
                        'change_num',
                        'accept_num',
                        'close_num',
                        'review_num',
                        'participants_count',
                        'title_words',
                        'body_words',
                        'has_bug',
                        'has_document',
                        'has_feature',
                        'has_improve',
                        'has_refactor',
                        'deletions_per_week',
                        'additions_per_week',
                        'changes_per_week',
                        'per_lines_deleted_week_days',
                        'per_lines_added_week_days',
                        'per_lines_changed_week_days',
                        'deletions_per_pr',
                        'additions_per_pr',
                        'changes_per_pr',
                        'commits_average',
                        'comments_per_closed_pr',
                        'comments_per_merged_pr',
                        'close_latency',
                        'merge_latency']].to_numpy()
        
        ##预测标签
        # y = nodes_data[['response_speed','if_merged']].to_numpy()
        y = nodes_data[['response_speed']].to_numpy()
        

        # 读节点id->边
        edges_src = edges_data['SrcId'].to_numpy()
        edges_dst = edges_data['DesId'].to_numpy()
        
        
        num_nodes = nodes_data.shape[0]

        n_train = int(num_nodes * 0.8)
        train_mask = np.zeros(num_nodes, dtype=bool)
        test_mask = np.zeros(num_nodes, dtype=bool)
            
        # 划分的工具就是mask
        train_mask[:n_train] = True
        test_mask[n_train:] = True

        adjacency_dict=dict()

        ##生成邻接表
        record=0
        tmp=[]
        for i,srcId in enumerate(edges_src):
            if srcId != record:
                adjacency_dict[record]=tmp
                record=srcId
                tmp=[]
            tmp.append(edges_dst[i])
            if i==(len(edges_src)-1):
                adjacency_dict[srcId]=tmp   

          

        ##打印图的基本信息
        print("Node's feature shape: ", x.shape)
        print("Node's label shape: ", y.shape)
        print("Adjacency's shape: ", len(adjacency_dict))
        print("Number of training nodes: ", train_mask.sum())
        print("Number of test nodes: ", test_mask.sum())

        return Data(x=x, y=y, adjacency_dict=adjacency_dict,
                    train_mask=train_mask, test_mask=test_mask)

    @property
    def data(self):
        """返回Data数据对象，包括x, y, adjacency, train_mask, test_mask"""
        return self._data
    

# data=GraphData_train().data
# print(data.adjacency_dict)
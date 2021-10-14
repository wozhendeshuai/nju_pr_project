# PR优先级

此项目主要用于存储爬虫，与GNN相关代码

目录结构：
- mysql_python，用于测试python与数据库之间的相关操作
- spider，用于测试调用GitHub API相关操作，与书写相关爬虫程序
- utils，用于存储相关工具类，工具方法，具体看名称
- pyg_learning，用于存储相关图神经网络学习代码

相关库的按装
```python
pip3 install torch==1.9.1+cu102 torchvision==0.10.1+cu102 torchaudio===0.9.1 -f https://download.pytorch.org/whl/torch_stable.html
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f https://data.pyg.org/whl/torch-1.9.0+cu102.html
```

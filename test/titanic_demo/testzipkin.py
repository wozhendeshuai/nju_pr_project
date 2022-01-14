import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import seaborn as sns
from utils.print_photo import showBN
from pgmpy.models import BayesianNetwork, BayesianModel
from pgmpy.estimators import BayesianEstimator
# 用结构学习建立模型
# %%
from pgmpy.estimators import HillClimbSearch
from pgmpy.estimators import K2Score, BicScore

# combine train and test set.
train = pd.read_csv(
    'E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\zipkin_bayes_rank_format_train_data.csv')
test = pd.read_csv(
    'E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\zipkin_bayes_rank_format_train_data.csv')
full = pd.concat([train, test], ignore_index=True)

dataset = full.drop(columns=['pr_number',
                             # 'deletions_per_week',
                             # 'additions_per_week',
                             # 'changes_per_week',
                             # 'per_lines_deleted_week_days',
                             # 'per_lines_added_week_days',
                             # 'per_lines_changed_week_days',
                             # 'deletions_per_pr',
                             # 'additions_per_pr',
                             # 'changes_per_pr',
                             # 'commits_average',
                             # 'comments_per_closed_pr',
                             # 'comments_per_merged_pr',
                             # 'close_latency',
                             # 'merge_latency', 'self_accept_rate',
                             # 'self_closed_num_rate',
                             # 'self_contribution_rate',
                             # 'project_accept_rate',
                             # 'file_changed_num',
                             # 'has_assignees_content'
                             ])
dataset.dropna(inplace=True)
dataset['priorities_number'] = dataset['priorities_number'].astype(int)
# dataset=pd.concat([dataset, pd.DataFrame(columns=['Pri'])])
train = dataset[:2100]
test = dataset[2100:]

print(train.head())

directory = "E:\\pythonProject\\nju_pr_project\\test\\titanic_demo\\picture"

hc = HillClimbSearch(train)  # HillClimbSearch(train, scoring_method=BicScore(train))
best_model = hc.estimate(scoring_method="k2score", max_indegree=4, max_iter=int(1e4))
print(best_model.edges())
showBN(best_model, True, "zipkin_HillClimbSearch.gv", directory)
best_model = BayesianModel(best_model.edges())
best_model.fit(train, estimator=BayesianEstimator, prior_type="BDeu")  # default equivalent_sample_size=5
for key in best_model.nodes:
    print(key)
best_model.save(filename="zipkin_HillClimbSearch.bif", filetype="bif")
# best_model=BayesianNetwork.load(filename="zipkin_HillClimbSearch.bif", filetype="bif")
predict_data = test.drop(columns='priorities_number', axis=1)
print(set(predict_data.columns) - set(best_model.nodes()))
temp_data = predict_data
temp_set = set(predict_data.columns) - set(best_model.nodes())
for key in temp_set:
    temp_data = predict_data.drop(columns=key, axis=1)
y_pred = best_model.predict(temp_data, n_jobs=1)

print(y_pred)
y_pred.to_csv("./zipkin.csv", index=0)

# # (y_pred['Survived']==test['Survived']).sum()/len(test)#测试集精度
# # 预测原test集并保存csv
# # %%
# kaggle_test = full.drop(columns=['Embarked', 'Name', 'Parch', 'PassengerId', 'SibSp', 'Ticket', 'Title'])
# kaggle_test = kaggle_test[kaggle_test['Survived'].isna()]
# kaggle_test = kaggle_test.drop(columns=['Survived'], axis=1)
# kaggle_test_pred = best_model.predict(kaggle_test)
# kaggle_test_pred = best_model.predict(kaggle_test)
# %%
# kaggle_test_pred = kaggle_test_pred.reindex(columns=['PassengerId', 'Survived'])
# kaggle_test_pred['PassengerId'] = np.linspace(892, 1309, 1309 - 892 + 1, dtype=np.int)
# kaggle_test_pred
# kaggle_test_pred.to_csv('./kaggle_test_pred.csv', index=0)

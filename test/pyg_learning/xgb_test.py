import xgboost as xgb
from xgboost import DMatrix
from sklearn.datasets import load_svmlight_file


#  This script demonstrate how to do ranking with xgboost.train
x_train, y_train = load_svmlight_file("angular.js_train_data")
x_test, y_test = load_svmlight_file("angular.js_test_data")

group_train = []
with open("angular.js_train_group_data", "r") as f:
    data = f.readlines()
    for line in data:
        group_train.append(int(line.split("\n")[0]))



train_dmatrix = DMatrix(x_train, y_train)
# valid_dmatrix = DMatrix(x_valid, y_valid)
test_dmatrix = DMatrix(x_test)

train_dmatrix.set_group(group_train)
# valid_dmatrix.set_group(group_valid)
ranktype="pairwise"
params = {'objective': 'rank:'+ranktype, 'eta': 0.1, 'gamma': 1.0,
          'min_child_weight': 0.1, 'max_depth': 6}
xgb_model = xgb.train(params, train_dmatrix, num_boost_round=4,
                      evals=[(train_dmatrix, 'validation')])
pred = xgb_model.predict(test_dmatrix)
xgb_model.save_model('xgb.json')
tar = xgb.Booster(model_file='xgb.json')
pre=tar.predict(test_dmatrix)

for temp in pre:
    print(temp)



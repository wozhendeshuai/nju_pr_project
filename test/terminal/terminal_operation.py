import os

repo_name ="angular.js"#"tensorflow"   # "symfony"# #"spring-boot"#"spring-framework"#"rails"
# 文件路径
jar_path = "E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar"
train_data_path = "E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\" + repo_name + "_svm_rank_format_train_data.txt"
test_data_path = "E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\" + repo_name + "_svm_rank_format_test_data.txt"
model_path = "E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\" + repo_name + "_randomforest_model.txt"

# rank_model_str = " java -jar E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar " \
#                  "-train E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_train_data.txt " \
#                  "-test E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_test_data.txt  " \
#                  "-ranker 8 -metric2t NDCG@10 -metric2T NDCG@10 -save E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\angular.js_randomforest_model.txt"

rank_model_str = "java -jar " + jar_path + " -train " + train_data_path + " -test " + test_data_path + " -ranker 8 -metric2t NDCG@10 -metric2T NDCG@10 -save " + model_path
recv = os.popen(rank_model_str)
# re_rank_str = "java -jar E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar -load E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\angular.js_randomforest_model.txt -rank E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_data.txt -indri E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_myScoreFile.txt"
print("=======")
print(recv.read())
# recv = os.popen(re_rank_str)
# print("=======")
# print(recv.read())

# shuffle_str="java -cp E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar" \
# " ciir.umass.edu.features.FeatureManager -input E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_data.txt -output E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\ -shuffle"
# recv = os.popen(shuffle_str)
# print("=======")
# print(recv.read())

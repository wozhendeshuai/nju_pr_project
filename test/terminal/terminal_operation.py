import os

rank_model_str = " java -jar E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar -train E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.jssvm_rank_format_data.txt -test E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.jssvm_rank_format_data.txt  -ranker 8 -metric2t NDCG@10 -metric2T ERR@10 -save E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\angular.js_randomforest_model.txt"
recv = os.popen(rank_model_str)
re_rank_str = "java -jar E:\\pythonProject\\nju_pr_project\\baseline\\RankLib-2.16.jar -load E:\pythonProject\\nju_pr_project\\baseline\\rank_model\\angular.js_randomforest_model.txt -rank E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.jssvm_rank_format_data.txt -indri E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_myScoreFile.txt"
print("=======")
print(recv.read())
recv = os.popen(re_rank_str)
print("=======")
print(recv.read())
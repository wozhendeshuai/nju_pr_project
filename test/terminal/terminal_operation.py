import os

recv = os.popen(
    "e: && cd E:\pythonProject\\nju_pr_project\\baseline && java -jar RankLib-2.16.jar -load MQ2008/models/mymodel.txt -rank MQ2008/test/result.txt -indri MQ2008/test/myNewRankList2.txt")
print("=======")
print(recv.read())

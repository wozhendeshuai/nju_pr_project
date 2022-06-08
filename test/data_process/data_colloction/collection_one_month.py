import csv
import time
from utils.path_exist import path_exists_or_create

headers = ['day',
           'day_create',
           'day_close',
           'day_workload'
           ]

reader = csv.reader(open("./result/tensorflow_repo_per_collections.csv", "r"))
month_dict={}
for item in reader:
    if reader.line_num == 1:
        continue
    if month_dict.__contains__(item[0][0:7]):
        month_dict[item[0][0:7]]["month_create"]=month_dict[item[0][0:7]]["month_create"]+int(item[1])
        month_dict[item[0][0:7]]["month_close"] = month_dict[item[0][0:7]]["month_close"] + int(item[2])
        month_dict[item[0][0:7]]["month_workload"] = month_dict[item[0][0:7]]["month_workload"] + int(item[3])
        month_dict[item[0][0:7]]["count"] = month_dict[item[0][0:7]]["count"]+1
    else:
        month_dict[item[0][0:7]]={}
        month_dict[item[0][0:7]]["month_create"] = int(item[1])
        month_dict[item[0][0:7]]["month_close"] =int(item[2])
        month_dict[item[0][0:7]]["month_workload"] = int(item[3])
        month_dict[item[0][0:7]]["count"] = 1
    print(item)
print(month_dict)
headers = ['month',
           '平均每日创建PR数',
           '平均每日关闭PR数',
           '平均每日工作量'
           ]
with open("./result/tensorflow_repo_per_collections_month.csv",
          'w+', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, dialect='excel')
    writer.writerow(headers)
    f.close()
for temp in month_dict.keys():
    month_dict[temp]['count']
    item_date = [temp,
                 month_dict[temp]['month_create']/month_dict[temp]['count'],
                 month_dict[temp]['month_close']/month_dict[temp]['count'],
                 month_dict[temp]['month_workload']/month_dict[temp]['count']]
    with open("./result/tensorflow_repo_per_collections_month.csv", 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(item_date)
        f.close()
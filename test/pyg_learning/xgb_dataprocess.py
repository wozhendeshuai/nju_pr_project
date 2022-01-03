import sys


def save_data(group_data, output_feature, output_group):
    if len(group_data) == 0:
        return

    output_group.write(str(len(group_data)) + "\n")
    for data in group_data:
        # only include nonzero features
        feats = [p for p in data[2:] if float(p.split(':')[1]) != 0.0]
        output_feature.write(data[0] + " " + " ".join(feats) + "\n")

# E:\\pythonProject\\nju_pr_project\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_train_data.txt
fi = open("E:\\pythonProject\\nju_pr_project\\data_processing_engineering\\rank_data\\angular.js_svm_rank_format_test_data.txt")
output_feature = open("angular.js_test_data", "w")
output_group = open("angular.js_test_group_data", "w")

group_data = []
group = ""
for line in fi:
    if not line:
        break
    if "#" in line:
        line = line[:line.index("#")]
    splits = line.strip().split(" ")
    if splits[1] != group:
        save_data(group_data, output_feature, output_group)
        group_data = []
    group = splits[1]
    group_data.append(splits)

save_data(group_data, output_feature, output_group)

fi.close()
output_feature.close()
output_group.close()

from pymysql import NULL
import getData
import os
basedir = os.path.abspath(os.path.dirname(__file__))


file_path_data=getData.getDataFromSql(
    "select pr_number,changed_file_name from pr_file"
)

##字典保存pr修改的文件路径 （pr_number,文件路径）
file_path_dict=[]
file_path_dict.append((file_path_data[0][0],[file_path_data[0][1]]))
pr_number=file_path_data[0][0]
file_path_dict=dict(file_path_dict)

for i in range(1,len(file_path_data)):
    if file_path_data[i][0]==pr_number:
        file_path_dict[pr_number].append(file_path_data[i][1])
    else:
        file_path_dict[file_path_data[i][0]]=[file_path_data[i][1]]
        pr_number=file_path_data[i][0]


raw_data=getData.getDataFromSql(
    "select pr_number from pr_self"
)
count=0
process_data=[]
for i in raw_data:
    process_data.append([i[0],count])
    count+=1

# print(process_data)

f1 = open(basedir+"/edge_filepath_source.txt",'w')
f2 = open(basedir+"/edge_filepath_destination.txt",'w')


print("processing...")
for i in process_data:
    if i[0] in file_path_dict.keys():
        i_path=file_path_dict[i[0]]
        for j in process_data:
            if j[0] in file_path_dict.keys() and j[0]!=i[0]:
                j_path=file_path_dict[j[0]]
                for k in i_path:
                    if k in j_path:
                        f1.writelines(str(i[1])+'\n')
                        f2.writelines(str(j[1])+'\n')
                        break

f1.close()
f2.close()
print("done!")









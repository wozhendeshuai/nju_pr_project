import json


def get_label_count(labels_dict):
    """
       计算每个pr中的label的数量
       labels_dict
       {
            52950: '{"0": {"id": 300136587, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/cla:%20yes", "name": "cla: yes", "color": "009800", "default": false, "node_id": "MDU6TGFiZWwzMDAxMzY1ODc=", "description": null}, "1": {"id": 1169365682, "url": "https://api.github.com/repos/tensorflow/tensorflow/labels/size:L", "name": "size:L", "color": "adafea", "default": false, "node_id": "MDU6TGFiZWwxMTY5MzY1Njgy", "description": "CL Change Size: Large"}}'
       }
       转为json后计算json的长度
       """
    re_dict = {}
    for key in labels_dict.keys():
        labels_json = json.loads(labels_dict[key])
        re_dict[key] = len(labels_json)
    return re_dict

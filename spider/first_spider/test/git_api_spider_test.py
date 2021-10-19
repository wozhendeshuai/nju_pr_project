import requests
from utils.access_token import get_token

url = 'https://api.github.com/repos/nodejs/node/pulls/13'
access_token = get_token()
headers = {
    'Authorization': 'token ' + access_token
}
r = requests.get(url, headers=headers)

print("Status Code:", r.status_code)
print('status header', r.headers)
print(r.json())

# import  json
# json_str=pr_r.json()
# print(json_str)
# print('pr_r body: ',pr_r.json()['body'])
# print('json body: ',json_str['body'])
# print('json user login: ',json_str['user']['login'])
# import requests
# import pygal
# from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS
#
# url = 'https://api.github.com/search/repositories?q=language:python&sort=stars'
#
# pr_r = requests.get(url)
#
# print("Status Code:", pr_r.status_code)
#
# response_dict = pr_r.json()
#
# print("Total repositories:", response_dict['total_count'])
#
# repo_dicts = response_dict['items']
# # print("Repositories returned:" ,len(repo_dicts))
#
#
# names, plot_dicts = [], []
# for repo_dict in repo_dicts:
#     names.append(repo_dict['name'])
#
#     if repo_dict['description']:
#         plot_dict = {
#             'value': repo_dict['stargazers_count'],
#             'label': repo_dict['description'],
#         }
#         plot_dicts.append(plot_dict)
#     else:
#         plot_dict = {
#             'value': repo_dict['stargazers_count'],
#             'label': 'None'
#         }
#         plot_dicts.append(plot_dict)
#  # 格式设置
# my_style = LS('#333366', base_style=LCS)
# my_config = pygal.Config()
# my_config.x_label_rotation = 45
# my_config.show_legend = False
# my_config.title_font_size = 24
# my_config.label_font_size = 14
# my_config.major_label_font_size = 18
# my_config.truncate_label = 15
# my_config.show_y_guides = False
# my_config.width = 1000
#
# chart = pygal.Bar(my_config, style=my_style)
# chart.title = 'Most-Starred Python Project on Github'
# chart.x_labels = names
# chart.add('', plot_dicts)
# chart.render_to_file('python_repos.svg')

from spider.project_spider.spider_cloud_pr_file_for_java import get_pr_file_info
from spider.project_spider.spider_cloud_pr_repo_for_java import get_repo_info
from spider.project_spider.spider_cloud_pr_self_for_java import get_pr_self_info
from spider.project_spider.spider_cloud_pr_user_for_java import get_pr_user_info
from utils.access_token import get_token

if __name__ == '__main__':
    # 此部分可修改，用于控制进程
    index = 0
    max_pr_num = 700
    #helix-editor/helix hibernate/hibernate-orm/incubator-heron "openzipkin/zipkin"
    owner_name ="apache"#"helix-editor"#"hibernate"#"Homebrew"#"apache"#"Ipython" #"apache"  # "Katello"#"kubernetes"#"mdn"#"openzipkin"#"laravel" #"apache"#  # "spring-projects"  # "symfony"#"rails"#"angular" #"tensorflow"
    repo_name ="guacamole-client" #"helix"#"hibernate-orm"#"homebrew-cask"#"incubator-heron"#"Ipython"#"kafka"  # "Katello"#"kubernetes"#"kuma"#"zipkin"#"laravel" #"lucene-solr"#  # "spring-framework"  # "spring-boot" #"symfony"#"rails"#"angular.js"#"tensorflow"

    access_token = get_token()
    headers = {
        'Authorization': 'token ' + access_token
    }

    get_repo_info(index, max_pr_num, owner_name, repo_name, headers)
    print(owner_name + ": repo " + repo_name + "—===============================仓库信息存储完毕=======================")
    print(owner_name + ": repo " + repo_name + "—===============================仓库信息存储完毕=======================")
    print(owner_name + ": repo " + repo_name + "—===============================仓库信息存储完毕=======================")
    get_pr_self_info(index, max_pr_num, owner_name, repo_name, headers)
    print(owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")
    print(owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")
    print(owner_name + ": pr_self " + repo_name + "—===============================pr_self信息存储完毕=======================")
    get_pr_file_info(index, max_pr_num, owner_name, repo_name, headers)
    print( owner_name + ": pr_file " + repo_name + "—===============================pr_file信息存储完毕=======================")
    print(owner_name + ": pr_file " + repo_name + "—===============================pr_file信息存储完毕=======================")
    print( owner_name + ": pr_file " + repo_name + "—===============================pr_file信息存储完毕=======================")
    get_pr_user_info(index, max_pr_num, owner_name, repo_name, headers)
    print( owner_name + ": pr_user " + repo_name + "—===============================pr_user信息存储完毕=======================")
    print( owner_name + ": pr_user " + repo_name + "—===============================pr_user信息存储完毕=======================")
    print(owner_name + ": pr_user " + repo_name + "—===============================pr_user信息存储完毕=======================")

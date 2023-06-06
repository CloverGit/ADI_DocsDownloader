import requests
import json
import os
from multiprocessing.pool import Pool as ThreadPool

proxies = {
    "http": "http://127.0.0.1:4585",
    "https": "http://127.0.0.1:4585",
}


def get_document_info(keyword):
    url = "https://www.analog.com/zh/client/Search/PostSearchResultsJson"
    payload = '{\"Content\":\"' + keyword + '\",\"PageSize\":10,\"PageStart\":0,\"SortBy\":\"customdate_s\",\"Order\":\"relevancy\"}'
    headers = {
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    # 发送 POST 请求
    response = requests.request("POST", url, headers=headers, data=payload, proxies=proxies)

    # 搜索结果存储在 response.text 的 ResultPayload 中
    result_payload = json.loads(response.text)['GetAllSearchResultsResult']['ResultPayload']

    # 在搜索结果中进行搜索 PageTitle 内容中包含 'mt-002' 的结果(不区分大小写)
    for result in result_payload:
        if keyword in result['PageTitle'].lower():
            page_title = result['PageTitle']
            product_category = result['ProductCategory']
            absolute_url = result['AbsoluteURL']
            print(page_title, product_category, absolute_url)
            return page_title, product_category, absolute_url
    else:
        print('未找到: ' + keyword)
        return None


def download_document(info, path):
    url = info[2]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    # 设置和创建路径
    name = info[0] + '.pdf'
    # 替换文件名特殊符号/\:*?"<>|, 替换为中文符号
    name = name.replace('/', '／').replace('\\', '＼').replace(':', '：').replace('*', '＊').replace('?', '？').replace(
        '"', '＂').replace('<', '＜').replace('>', '＞').replace('|', '｜')
    # 去掉冒号后面所有不必要的空格
    while '： ' in name:
        name = name.replace('： ', '：')
    path = path + info[1] + '/'
    full_path = path + name
    os.path.exists(path) or os.makedirs(path)
    if os.path.exists(full_path):
        print('文件已存在: ' + full_path)
        return

    # 下载文件
    try:
        response = requests.get(url, stream=True, allow_redirects=False, headers=headers, proxies=proxies)
        print('保存到: ' + full_path + '...', end=' ')
    except:
        print("失败")
    else:
        print("成功")
        with open(full_path, 'wb') as f:
            f.write(response.content)
            f.close()


def download_mt(doc_num_list):
    info = [None] * doc_num_list[0]
    save_path = 'C:/Users/CloverGit/Downloads/ADI_MT/'
    for num in doc_num_list:
        keyword = 'mt-' + str(num).zfill(3)

        info.append(get_document_info(keyword))
        if info[num] is not None:
            download_document(info[num], save_path)


if __name__ == '__main__':
    pool = ThreadPool(16)
    mt_num_list = range(1, 999)
    # download_mt(mt_num_list)
    pool.imap(download_mt, [mt_num_list])

    while True:
        pass

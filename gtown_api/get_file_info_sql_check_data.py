# 获取
import requests
import json
import re

# 请求的 URL
url = 'https://archery.a.com.cn/query/'

# 请求头
headers = {
    'Cookie': 'csrftoken=VJWi1BzIPE4NRBtKXkmNRSZslFnpZ6Ab; sessionid=duxxt6tiyf50rp9ch8gpm76cdzybjf59',
    'X-CSRFToken': 'VJWi1BzIPE4NRBtKXkmNRSZslFnpZ6Ab',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

# 存储扩展名的集合，用于去重
extensions = set()

# 偏移量，初始为 0
offset = 0

# 打开文件用于存储 file_path 和扩展名
with open('file_paths.txt', 'w', encoding='utf-8') as file_paths_file, \
        open('extensions.txt', 'w', encoding='utf-8') as extensions_file:
    while True:
        # 构建请求数据
        data = {
            'instance_name': 'prod-ob-omp',
            'db_name': 'omp_product_sec',
            'schema_name': '',
            'tb_name': 'file_info',
            'sql_content': f'SELECT id, file_path FROM omp_product_sec.file_info LIMIT 1000 OFFSET {offset};',
            'limit_num': 0
        }

        # 发送请求
        response = requests.post(url, headers=headers, data=data)

        # 解析响应
        try:
            response_data = response.json()
            rows = response_data.get('data', {}).get('rows', [])

            # 如果没有数据，退出循环
            if not rows:
                break

            # 处理每一行数据
            for row in rows:
                file_path = row[1]
                # 将 file_path 写入文件
                file_paths_file.write(file_path + '\n')

                try:
                    # 尝试解析为 JSON 数组
                    file_path_data = json.loads(file_path)
                    if isinstance(file_path_data, list):
                        for item in file_path_data:
                            url = item.get('url', '')
                            # 提取扩展名
                            match = re.search(r'\.([^./?]+)(?:\?|$)', url)
                            if match:
                                ext = match.group(1).lower()
                                extensions.add(ext)
                                # 将扩展名写入文件
                                extensions_file.write(ext + '\n')
                    elif isinstance(file_path_data, dict):
                        url = file_path_data.get('url', '')
                        # 提取扩展名
                        match = re.search(r'\.([^./?]+)(?:\?|$)', url)
                        if match:
                            ext = match.group(1).lower()
                            extensions.add(ext)
                            # 将扩展名写入文件
                            extensions_file.write(ext + '\n')
                except json.JSONDecodeError:
                    continue

            # 增加偏移量
            offset += 1000

        except json.JSONDecodeError:
            print("无法解析响应为 JSON 数据。")
            break

# 打印去重后的扩展名
print("去重后的扩展名：")
for ext in extensions:
    print(ext)

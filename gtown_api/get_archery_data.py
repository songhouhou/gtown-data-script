# 查询Archery数据
import requests
import csv
from datetime import datetime
import time

# 请替换为实际的请求 URL
URL = "https://archery.g-town.com.cn/query/"

def main():
    cookie = ""
    xCSRFToken = ""
    sql = ""

    # 设置请求头
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "Cookie": cookie,
        "X-CSRFToken": xCSRFToken,
        "X-Requested-With": "XMLHttpRequest"
    }

    offset = 0
    column_has_write = False
    file_name = f"data_export{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    with open(file_name, mode='w', newline='', encoding='utf-8') as file_writer:
        csv_writer = csv.writer(file_writer)

        while True:
            # 构建请求数据
            data = {
                "instance_name": "prod-ob-omp",
                "db_name": "omp_product_sec",
                "schema_name": "",
                "tb_name": "file_info",
                "sql_content": f"{sql} LIMIT 1000 OFFSET {offset};",
                "limit_num": "0"
            }

            # 发送请求
            response = requests.post(URL, headers=headers, data=data)
            response_body = response.json()

            # 解析响应
            data_obj = response_body.get("data")
            if data_obj is None:
                break

            column_list = data_obj.get("column_list")
            if not column_has_write:
                csv_writer.writerow(column_list)
                column_has_write = True

            rows = data_obj.get("rows")
            if rows is None or not rows:
                break

            # 处理每一行数据
            for row in rows:
                csv_writer.writerow(row)
                print(row)

            # 增加偏移量
            offset += 1000
            time.sleep(0.1)

if __name__ == "__main__":
    main()
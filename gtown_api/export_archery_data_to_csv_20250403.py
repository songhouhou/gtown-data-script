# # 导出Archery数据到 CSV 文件
# import csv
# import time
# from datetime import datetime
#
# import requests
#
# # 请替换为实际的请求 URL
# URL = "https://archery.g-town.com.cn/query/"
#
#
# def main():
#     cookie = "csrftoken=RAS1Awy7No2RQFYskvWxcjW9CCs9FwbD; sessionid=7fs71xg89j8l0rai1in5lzvh4brvwvfe"
#     xCSRFToken = "RAS1Awy7No2RQFYskvWxcjW9CCs9FwbD"
#
#     instance_name = "prod-ob-omp"
#     db_name = "omp_order_sec"
#     sql = "select  res_url from  upload_download_records where  res_url is not null   and res_url != ''"
#
#     # 设置请求头
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
#         "Cookie": cookie,
#         "X-CSRFToken": xCSRFToken,
#         "X-Requested-With": "XMLHttpRequest"
#     }
#
#     offset = 0
#     column_has_write = False
#     file_name = f"data_export_{db_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"
#     result_set = set()
#     with open(file_name, mode='w', newline='', encoding='utf-8') as file_writer:
#         csv_writer = csv.writer(file_writer)
#
#         while True:
#             # 构建请求数据
#             data = {
#                 "instance_name": instance_name,
#                 "db_name": db_name,
#                 "schema_name": "",
#                 "tb_name": "",
#                 "sql_content": f"{sql} LIMIT 1000 OFFSET {offset};",
#                 "limit_num": "0"
#             }
#
#             # 发送请求
#             response = requests.post(URL, headers=headers, data=data)
#             response_body = response.json()
#
#             # 解析响应
#             data_obj = response_body.get("data")
#             if data_obj is None:
#                 break
#
#             column_list = data_obj.get("column_list")
#             if not column_has_write:
#                 csv_writer.writerow(column_list)
#                 column_has_write = True
#
#             rows = data_obj.get("rows")
#             if rows is None or not rows:
#                 break
#
#             # 处理每一行数据
#             for row in rows:
#                 csv_writer.writerow(row)
#                 # print(row)
#                 print(row[0].split("/")[0])
#                 result_set.add(row[0].split("/")[0])
#
#             # 增加偏移量
#             offset += 1000
#             time.sleep(0.1)
#     print(result_set)
#
#
# if __name__ == "__main__":
#     main()

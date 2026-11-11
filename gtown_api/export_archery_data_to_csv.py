# 导出Archery数据到 CSV 文件
import csv
import time
from datetime import datetime


import requests

# 请替换为实际的请求 URL
URL = "https://archery.g-town.com.cn/query/"


def main():
    cookie = "csrftoken=vcC8BXtBco0hvSVpYVOKowAxSC80jBHA; sessionid=jdwm7k3c9o8rknz06t65mp7k88xfz35g"
    xCSRFToken = cookie.split("csrftoken=")[1].split(";")[0].strip()

    instance_name = "prod-ob-omp"
    db_name = "omp_order_sec"
    ####末尾不能加;
    ####
    sql = """
SELECT o.order_no, o.main_order_no, o.order_type, o.order_status,
       o.channel_code, o.supplier_code, o.supplier_item_code,
       o.cost_avg_price, o.create_time,
       d.supplier_settlement_type, d.supplier_settlement_time
FROM fms_order_sec.orders o
JOIN fms_order_sec.orders_main m ON m.order_no = o.main_order_no
JOIN fms_order_sec.orders_detail_extra d ON d.order_no = o.order_no
WHERE o.create_time >= '2026-01-01 00:00:00'
  AND o.order_type IN (7, 12)
  AND o.order_status = 2
  AND d.supplier_settlement_time IS NOT NULL
  AND (m.landing_type_no <> '1' OR m.landing_type_no IS NULL)
  AND (m.jc_order_no IS NULL OR m.jc_order_no = '')
  AND NOT EXISTS (
      SELECT 1
      FROM omp_product_sec.omp_purchase_order po
      WHERE po.order_detail_no = o.order_no
        AND po.is_del = 0
  );
"""
    sql = sql.replace(";", "")
    # 设置请求头
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "Cookie": cookie,
        "X-CSRFToken": xCSRFToken,
        "X-Requested-With": "XMLHttpRequest"
    }

    offset = 0
    # page_size = 20000
    # page_size = 1000
    page_size = 100
    column_has_write = False
    file_name = f"data_export_{db_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"

    with open(file_name, mode='w', newline='', encoding='utf-8') as file_writer:
        csv_writer = csv.writer(file_writer)
        cnt = 1
        while True:
            print(f"正在处理第 {cnt} 页数据...")
            # 构建请求数据
            data = {
                "instance_name": instance_name,
                "db_name": db_name,
                "schema_name": "",
                "tb_name": "",
                "sql_content": f"{sql} LIMIT {page_size} OFFSET {offset};",
                "limit_num": "0"
            }

            # 发送请求
            response = requests.post(URL, headers=headers, data=data)
            response_body = response.json()
            # print(response_body)

            # 解析响应
            data_obj = response_body.get("data")
            # print(data_obj)
            if data_obj is None:
                break

            # print(data_obj)
            column_list = data_obj.get("column_list")
            # print(column_list)
            if not column_has_write:
                csv_writer.writerow(column_list)
                column_has_write = True

            rows = data_obj.get("rows")
            # print(rows)
            if rows is None or not rows:
                break

            # 处理每一行数据
            for row in rows:
                csv_writer.writerow(row)
                # print(row)

            # 增加偏移量
            offset += page_size
            time.sleep(0.1)
            # break
            cnt += 1


if __name__ == "__main__":
    main()

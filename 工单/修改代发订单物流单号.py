import requests
import pandas as pd
import json

# 读取 Excel 文件，假设文件名为 example.xlsx，根据实际情况修改
excel_file = pd.ExcelFile('C:\\Users\\houhou.song\\Downloads\\修改物流单号1126.xlsx')

# 获取指定工作表中的数据
df = excel_file.parse('Sheet1')

url = "https://omp2-api.g-town.com.cn/scm-order/order/update-carrierNo"
token= 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGFnIjoiMTkzODYyODQ0MTU5NDc5NDY4MzczOTQ1NDMwNjAxMTk1NTQ4Nzc2NzI0MjkyMTA0OTc4MDUxOTE4NjkzMTYwNjcwNDA0MDIwMDUzMjU4NTgzODc4MTg0NjY0NDY0NDM0NjE4MzkyNzg2Njk1NTg2OTM5OTkwNjQxNzA1NDQzMTEyMzMyMDE4NDc1MjM5ODQ0OTQ0MjIyNTE1NjEyMDk0NTMwMzQ1NTQ3MTc3OTc4Nzk5MTI3MjEwNzMxNzc4OTE5NjA4NjI1MDkwODA4MjEzNzE2Mzk3NDgyOTk3ODg5MDE5MTgyMDY1ODAyMTY1MzY2MjQ4NDcwNTA1NTAwMDkzNzc5MTE5MzA2MTYwOTk4NTY1NDc4MzQwMDU2MTUzNzM0MDEwNTYyMjQzNzcxMjQ5MzQzODQ0NzA3MTcyNTYxNzgwNDUyNzI1NTM1MDAwMDQyMDUzNDA2MzAwMzIyMDgyODcxMjI1NTkyNTcyODY0Mjk2OTczMjM2OTU5OTgiLCJ1c2VyX25hbWUiOiJIb3Vob3UuU29uZyIsImVuIjoiSG91aG91LlNvbmciLCJlbXBsb3llZUlkIjoxMjU2MCwiY24iOiLlrovljprljpoiLCJ1c2VySWQiOjEyNjkwLCJhdXRob3JpdGllcyI6W10sImNsaWVudF9pZCI6ImY3ZDE2MGJlOWFlY2FkMDM0OGE4NWY3MzY0Njg0OGZmIiwicGhvbmUiOiIxODMqKioqNTUyNiIsInNjb3BlIjpbInJlYWQiLCJ3cml0ZSJdLCJ0ZW5hbnRJZCI6MTAwMDAsImRlcGFydG1lbnQiOiIvMTAwMDAvIiwianRpIjoiYWI3YTc2OTQtY2E3My00Yzc2LWEwZDUtMjM2YWNhZGUxOWU0IiwiZW1haWwiOiJob3Vob3Uuc29uZ0BnLXRvd24uY29tLmNuIn0.U3Abn3q1EX4HADGjEymcpbezfbtztd3iPQFX9g6NgX6KY0L7B9J_wCrtek1Z9KHT9bYXt4DIdMejKNVF-8HtiYaDEkEktysOrS1-7QBUmxPUbO-OAaGGnv0Cm4djbFIuLmmTd1LxjKc-lhyVdl2pyGT9NKorZd1TzN9ZaGTNoTNrzW5c5Wi9wNnoW1JhA-2r7ZphXnQCBIwhS6gyjTUL23TyaFrbyGm79okBq_lRbstCQ-xZdZ-WVHtJfdllW1IPIPElX_6-Q2FVAXPLsWiTl37VdqulY_AFlMU6KADUtgu478pxwB4eUCUYM9HYHF2CzxIcpI6UrhJkVIEpQq0scg'
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'authorization': token,
    'origin': 'https://omp2.g-town.com.cn',
    'priority': 'u=1, i',
    'referer': 'https://omp2.g-town.com.cn/',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'content-type': 'application/json'
}

# 循环遍历 DataFrame 的每一行
for index, row in df.iterrows():
    print(f"正在处理第 {index + 1} 行数据，数据：{row}")
    # "newCarrierCode": "gnxb",
    # "newCarrierName": "邮政国内小包",
    #  "newCarrierCode": "yunda",
    # "newCarrierName": "韵达快递",
    # "newCarrierCode": "yuantong",
    # "newCarrierName": "圆通",
    # "newCarrierCode": "SF",
    # "newCarrierName": "顺丰速运",
    payload = json.dumps({
        "id": int(row['scm_order_id']),  # 假设 Excel 中有 scm_order_id 列，根据实际列名修改
        "newCarrierNo": str(row['new_carrier_no']),  # 假设 Excel 中有 new_carrier_no 列，根据实际列名修改
        "newCarrierCode": "SF",
        "newCarrierName": "顺丰速运",
        "remark": "修改物流单号"
    }, ensure_ascii=False)

    print(f"第 {index + 1} 次请求参数: {payload}")
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(f"第 {index + 1} 次请求结果: {response.text}")

# 执行批量创建Archery SQL工单，通用版
# 功能说明：
# 1. 批量创建Archery SQL工单
# 2. 支持自定义cookie自动提取csrftoken和sessionid
# 3. 支持多批次SQL工单创建
# 4. 提供详细的执行日志和错误处理
import requests
import json
from typing import List, Dict
import time

# cookie
COOKIE = 'csrftoken=M2vUwMg6wCDO9JF0q3PX42e9cGEPdgjL; sessionid=vrt9nhiirvmoyfli8bmfb3dcna7j6o5y'

# 从cookie字符串中提取csrftoken和sessionid
def parse_cookie(cookie_str: str) -> Dict[str, str]:
    cookies = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

# 解析cookie
parsed_cookies = parse_cookie(COOKIE)
# [
#     {
#         "id": 43,
#         "db_type": "mysql",
#         "instance_name": "prod-ob-omp"
#     },
#     {
#         "id": 34,
#         "db_type": "mysql",
#         "instance_name": "预发-ob-omp"
#     }
# ]

# 配置项
CONFIG = {
    "api_url": "https://archery.g-town.com.cn/api/v1/workflow/",
    "headers": {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;",
        "origin": "https://archery.g-town.com.cn",
        "priority": "u=1, i",
        "referer": "https://archery.g-town.com.cn/",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "x-csrftoken": parsed_cookies.get("csrftoken", ""),
        "x-requested-with": "XMLHttpRequest"
    },
    "cookies": {
        "csrftoken": parsed_cookies.get("csrftoken", ""),
        "sessionid": parsed_cookies.get("sessionid", "")
    },
    # 基础工单配置
    "base_workflow": {
        "demand_url": "",
        "group_id": "1",
        "instance": "43", #prod-ob-omp43, 预发-ob-omp34
        "db_name": "omp_finance",
        "is_backup": False,
        "run_date_start": "",
        "run_date_end": "",
        "is_offline_export": 0
    }
}

# 定义所有需要创建工单的SQL批次
SQL_BATCHES: List[Dict[str, str]] = [
    {
        "name": "删除毛利中间表数据-12月第1批：12.01 - 12.07（7天）",
        "sql": "-- 删除毛利中间表数据-12月第1批：12.01 - 12.07（7天）\nDELETE FROM order_profit_integration\nWHERE create_time >= '2025-12-01 00:00:00' \n  AND create_time < '2025-12-08 00:00:00';"
    },
    {
        "name": "删除毛利中间表数据-12月第2批：12.08 - 12.14（7天）",
        "sql": "-- 删除毛利中间表数据-12月第2批：12.08 - 12.14（7天）\nDELETE FROM order_profit_integration\nWHERE create_time >= '2025-12-08 00:00:00' \n  AND create_time < '2025-12-15 00:00:00';"
    },
    {
        "name": "删除毛利中间表数据-12月第3批：12.15 - 12.21（7天）",
        "sql": "-- 删除毛利中间表数据-12月第3批：12.15 - 12.21（7天）\nDELETE FROM order_profit_integration\nWHERE create_time >= '2025-12-15 00:00:00' \n  AND create_time < '2025-12-22 00:00:00';"
    },
    {
        "name": "删除毛利中间表数据-12月第4批：12.22 - 12.31（10天）",
        "sql": "-- 删除毛利中间表数据-12月第4批：12.22 - 12.31（10天）\nDELETE FROM order_profit_integration\nWHERE create_time >= '2025-12-22 00:00:00' \n  AND create_time < '2026-01-01 00:00:00';"
    },
    {
        "name": "删除毛利中间表数据-1月第1批：01.01 - 01.07（7天）",
        "sql": "-- 删除毛利中间表数据-1月第1批：01.01 - 01.07（7天）\nDELETE FROM order_profit_integration\nWHERE create_time >= '2026-01-01 00:00:00' \n  AND create_time < '2026-01-08 00:00:00';"
    }
]


def create_workflow_ticket(workflow_name: str, sql_content: str) -> Dict:
    """
    创建单个工单
    :param workflow_name: 工单名称
    :param sql_content: SQL内容
    :return: 接口响应结果
    """
    # 构建请求体
    payload = {
        "workflow": {
            **CONFIG["base_workflow"],
            "workflow_name": workflow_name
        },
        "sql_content": sql_content
    }

    try:
        # 发送POST请求
        response = requests.post(
            url=CONFIG["api_url"],
            headers=CONFIG["headers"],
            cookies=CONFIG["cookies"],
            data=json.dumps(payload, ensure_ascii=False),
            timeout=30
        )

        # 解析响应
        response.raise_for_status()  # 抛出HTTP错误
        result = response.json()

        print(f"✅ 工单创建成功：{workflow_name}")
        print(f"   响应状态码：{response.status_code}")
        print(f"   响应内容：{json.dumps(result, ensure_ascii=False, indent=2)}\n")

        return result

    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ 工单创建失败（HTTP错误）：{workflow_name}"
        error_msg += f"\n   状态码：{response.status_code}" if 'response' in locals() else ""
        error_msg += f"\n   错误信息：{str(e)}"
        error_msg += f"\n   响应内容：{response.text if 'response' in locals() else '无'}\n"
        print(error_msg)

    except requests.exceptions.RequestException as e:
        print(f"❌ 工单创建失败（请求异常）：{workflow_name}")
        print(f"   错误信息：{str(e)}\n")

    except json.JSONDecodeError as e:
        print(f"❌ 响应解析失败：{workflow_name}")
        print(f"   响应内容：{response.text if 'response' in locals() else '无'}")
        print(f"   错误信息：{str(e)}\n")

    return {"status": "failed", "workflow_name": workflow_name}


def batch_create_tickets(batches: List[Dict[str, str]]) -> List[Dict]:
    """
    批量创建工单
    :param batches: 工单批次列表
    :return: 所有工单的创建结果
    """
    results = []
    print(f"开始批量创建工单，共 {len(batches)} 个批次\n")

    for idx, batch in enumerate(batches, 1):
        print(f"正在处理第 {idx}/{len(batches)} 个批次：{batch['name']}")
        result = create_workflow_ticket(batch['name'], batch['sql'])
        results.append(result)
        time.sleep(1)

    # 统计结果
    success_count = sum(1 for res in results if res.get("status") != "failed")
    print(f"\n批量创建完成！成功：{success_count}，失败：{len(results) - success_count}")

    return results


if __name__ == "__main__":
    # 执行批量创建
    batch_results = batch_create_tickets(SQL_BATCHES)
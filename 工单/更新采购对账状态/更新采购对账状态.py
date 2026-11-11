# 更新采购对账状态
import pandas as pd
import requests
import json
import time
from typing import List, Dict, Set

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
        "x-csrftoken": "eVDA1gav0QjFHnGs3GwyBeHJHgTH6z55",
        "x-requested-with": "XMLHttpRequest"
    },
    "cookies": {
        "csrftoken": "eVDA1gav0QjFHnGs3GwyBeHJHgTH6z55",
        "sessionid": "c6qreqreo19bs4u3fhyldnnhdvdxf9zy"
    },
    # 基础工单配置
    "base_workflow": {
        "demand_url": "https://gtpms.g-town.com.cn/biz/story-view-11498-0--story.html",
        "group_id": "1",
        "instance": "43", #prod-ob-omp43, 预发-ob-omp34
        "db_name": "omp_product_sec",
        "is_backup": False,
        "run_date_start": "",
        "run_date_end": "",
        "is_offline_export": 0
    }
}

def read_excel_data(file_path: str) -> pd.DataFrame:
    """
    读取Excel文件数据
    :param file_path: Excel文件路径
    :return: 读取的数据
    """
    try:
        df = pd.read_excel(file_path)
        print(f"✅ 成功读取Excel文件：{file_path}")
        print(f"   数据总行数：{len(df)}")
        print(f"   数据列名：{list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 读取Excel文件失败：{str(e)}")
        return pd.DataFrame()

def generate_sql_statements(df: pd.DataFrame) -> List[str]:
    """
    根据数据生成SQL语句
    :param df: 数据
    :return: SQL语句列表
    """
    if df.empty:
        return []
    
    # 确保必要的列存在
    required_columns = ['采购明细单号', '结算单号']
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ 缺少必要的列：{col}")
            return []
    
    # 使用字典去重，确保每个采购明细单号只保留最后一次出现的记录
    original_rows = len(df)
    unique_data_dict = {}
    
    for _, row in df.iterrows():
        purchase_details_no = row['采购明细单号']
        settlement_no = row['结算单号']
        
        if pd.isna(purchase_details_no) or pd.isna(settlement_no):
            print(f"⚠️  跳过空值行：采购明细单号={purchase_details_no}, 结算单号={settlement_no}")
            continue
        
        # 使用采购明细单号作为key，覆盖之前的记录，确保只保留最后一次出现的记录
        unique_data_dict[purchase_details_no] = settlement_no
    
    unique_rows = len(unique_data_dict)
    
    if original_rows > unique_rows:
        duplicates_removed = original_rows - unique_rows
        print(f"⚠️  去除了 {duplicates_removed} 条重复的采购明细单号记录，只保留最后一次出现的记录")
        print(f"   原始记录数：{original_rows}")
        print(f"   去重后记录数：{unique_rows}")
    
    # 生成SQL语句
    sql_statements = []
    
    for purchase_details_no, settlement_no in unique_data_dict.items():
        # 1. 更新采购结算单明细表
        sql1 = f"""
UPDATE `purchase_settlement_detail` 
SET 
    `reconciled_amount` = `reconcile_amount`,
    `reconciled_num` = `reconcile_num`,
    `remark` = 'https://gtpms.g-town.com.cn/biz/story-view-11498-0--story.html',
    `update_time` = '2025-12-31 14:02:00'  
WHERE `purchase_details_no` = '{purchase_details_no}' AND `settlement_no` = '{settlement_no}';"""
        
        # 2. 更新采购结算单表
        sql2 = f"""
UPDATE `purchase_settlement` ps 
JOIN (
    SELECT `reconcile_amount`, `reconcile_num` 
    FROM `purchase_settlement_detail` 
    WHERE `purchase_details_no` = '{purchase_details_no}' 
    AND `settlement_no` = '{settlement_no}'
) pd ON ps.`settlement_no` = '{settlement_no}'
SET 
    ps.`total_reconciled_amount` = ps.`total_reconciled_amount` + pd.`reconcile_amount`,
    ps.`total_reconciled_num` = ps.`total_reconciled_num` + pd.`reconcile_num`,
    ps.`remark` = 'https://gtpms.g-town.com.cn/biz/story-view-11498-0--story.html',
    ps.`update_time` = '2025-12-31 14:02:00'  
WHERE 
    ps.`settlement_no` = '{settlement_no}';
""".strip()  # strip()去除首尾空白，避免多余换行
        
        sql_statements.append(sql1)
        sql_statements.append(sql2)
    
    print(f"✅ 成功生成 {len(sql_statements)} 条SQL语句")
    return sql_statements

def write_sql_to_file(sql_statements: List[str], output_file: str) -> bool:
    """
    将SQL语句写入文件
    :param sql_statements: SQL语句列表
    :param output_file: 输出文件路径
    :return: 是否成功
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for sql in sql_statements:
                f.write(sql + '\n')
        print(f"✅ 成功将SQL语句写入文件：{output_file}")
        return True
    except Exception as e:
        print(f"❌ 写入SQL文件失败：{str(e)}")
        return False

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

def batch_call_archery_api(sql_statements: List[str], batch_size: int = 10) -> List[Dict]:
    """
    批量调用Archery接口
    :param sql_statements: SQL语句列表
    :param batch_size: 每批的SQL语句数量
    :return: 所有工单的创建结果
    """
    results = []
    
    if not sql_statements:
        print("❌ 没有SQL语句需要执行")
        return results
    
    # 将SQL语句分成批次
    batches = [sql_statements[i:i+batch_size] for i in range(0, len(sql_statements), batch_size)]
    
    print(f"✅ 将 {len(sql_statements)} 条SQL语句分成 {len(batches)} 个批次，每批 {batch_size} 条")
    
    # 逐个批次调用接口
    for idx, batch in enumerate(batches, 1):
        batch_sql = '\n'.join(batch)
        workflow_name = f"更新采购单为对账金额-批次{idx}/{len(batches)}"
        
        print(f"正在处理批次 {idx}/{len(batches)}...")
        print(f"   包含 {len(batch)} 条SQL语句")
        
        result = create_workflow_ticket(workflow_name, batch_sql)
        results.append(result)
        
        # 批次之间添加延迟
        if idx < len(batches):
            print(f"   等待 1 秒后处理下一批次...")
            time.sleep(5)
    
    # 统计结果
    success_count = sum(1 for res in results if res.get("status") != "failed")
    print(f"\n批量创建完成！成功：{success_count}，失败：{len(results) - success_count}")
    
    return results

def main():
    """
    主函数
    """
    # 配置参数
    excel_file = "/无需保留结算单.xlsx"
    output_file = "d:\\PythonProjects\\data-script\\结算单_generated_sql.txt"
    batch_size = 50000
    
    print("=" * 60)
    print("开始处理结算单数据...")
    print("=" * 60)
    
    # 1. 读取Excel数据
    df = read_excel_data(excel_file)
    if df.empty:
        print("❌ 没有数据需要处理")
        return
    
    # 2. 生成SQL语句
    sql_statements = generate_sql_statements(df)
    if not sql_statements:
        print("❌ 没有生成SQL语句")
        return
    
    # 3. 将SQL语句写入文件
    # write_sql_to_file(sql_statements, output_file)
    
    # 5. 批量调用Archery接口
    print("=" * 60)
    print("开始批量调用Archery接口...")
    print("=" * 60)
    batch_call_archery_api(sql_statements, batch_size)

    print("=" * 60)
    print("所有操作完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
EXCEL_FILE_PATH = r'C:\Users\houhou.song\Downloads\待修正银联数据.xlsx'

import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# ===================== 配置区（按需修改） =====================
OUTPUT_SQL_FILE = "omp_profit_report_update.sql"  # 输出SQL文件路径

# 数据库字段精度配置（完全匹配表结构）
PRECISION_12_4 = Decimal("0.0000")  # price、total_price、profit、forecast_profit
PRECISION_10_4 = Decimal("0.0000")  # profit_rate
PRECISION_10_2 = Decimal("0.00")    # tax
# =============================================================

def format_decimal(value, precision):
    """
    数值格式化工具：处理空值、四舍五入、避免科学计数法
    :param value: 原始数值
    :param precision: 精度配置
    :return: 格式化后的字符串，空值返回NULL
    """
    if pd.isna(value):
        return "NULL"
    try:
        # 转为Decimal类型，避免浮点精度问题
        decimal_val = Decimal(str(value)).quantize(precision, rounding=ROUND_HALF_UP)
        return str(decimal_val)
    except:
        return "NULL"

def escape_sql_string(value):
    """
    SQL字符串转义：处理单引号，避免语法错误
    :param value: 原始字符串
    :return: 转义后的字符串，空值返回空字符串
    """
    if pd.isna(value):
        return ""
    return str(value).replace("'", "''")

# 存储所有生成的SQL语句
sql_statements = []

# ---------------------- 处理Sheet1：销售数据（毛利类型=实际，profit_type=30） ----------------------
df_sales = pd.read_excel(EXCEL_FILE_PATH, sheet_name="Sheet1")
for idx, row in df_sales.iterrows():
    # 1. 提取WHERE条件字段
    sku_code = escape_sql_string(row["商品编码"])
    channel_code = escape_sql_string(row["项目编码"])
    # 日期格式化：转为YYYY-MM-DD标准格式
    create_time = row["毛利日期"].strftime("%Y-%m-%d") if pd.notna(row["毛利日期"]) else ""

    # 2. 提取待更新的6个字段
    price = format_decimal(row["修正后平均销售单价"], PRECISION_12_4)
    total_price = format_decimal(row["修正后结算总价"], PRECISION_12_4)
    tax = format_decimal(row["修正后增值税"], PRECISION_10_4)
    profit = format_decimal(row["修正后毛利（元）"], PRECISION_12_4)
    profit_rate = format_decimal(row["修正后毛利率"], PRECISION_10_4)
    forecast_profit = format_decimal(row["修正后预估毛利"], PRECISION_12_4)

    # 3. 生成UPDATE语句
    sql = f"""UPDATE omp_profit_report_v2 SET price = {price}, total_price = {total_price},  tax = {tax}, profit = {profit},profit_after_losses ={profit},    profit_rate = {profit_rate}, forecast_profit = {forecast_profit},    update_time = now() WHERE    channel_code = '{channel_code}'    AND sku_code = '{sku_code}'    AND create_time = '{create_time}'    AND profit_type = 30 AND is_del = 0;
"""
    sql_statements.append(sql)

# ---------------------- 写入SQL文件 ----------------------
with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as f:
    # 写入文件头注释
    f.write("-- 银联数据毛利报表修正UPDATE语句\n")
    f.write("-- 生成时间：2026-07-02\n")
    f.write("-- 数据说明：Sheet1销售数据 profit_type=30，Sheet2退换数据 profit_type=40\n")
    f.write(f"-- 总生成语句数：{len(sql_statements)} 条\n\n")
    # 写入所有SQL语句
    f.writelines(sql_statements)

print(f"✅ 生成完成！共生成 {len(sql_statements)} 条UPDATE语句")
print(f"📁 输出文件路径：{OUTPUT_SQL_FILE}")

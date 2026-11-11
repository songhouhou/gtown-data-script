import pandas as pd

INPUT = r"C:\Users\houhou.song\Downloads\待修复浦发银行数据.xlsx"
OUTPUT_SHEET1 = r"d:\PythonProjects\data-script\导出结果\sheet1_更新行方结算.sql"
OUTPUT_SHEET2 = r"d:\PythonProjects\data-script\导出结果\sheet2_更新行方结算.sql"

df1 = pd.read_excel(INPUT, sheet_name=0, dtype={'子订单号': str})
df2 = pd.read_excel(INPUT, sheet_name=1, dtype={'集采单号': str})

print(f"Sheet1 行数: {len(df1)}")
print(f"Sheet2 行数: {len(df2)}")

# ---- Sheet1: 根据订单号更新行方结算类型 + 行方结算时间更新为供应商结算时间 ----
sql1_lines = ["-- Sheet1: 根据订单号更新 channel_settlement_type 和 channel_settlement_time\n"]
for _, row in df1.iterrows():
    order_no = row['子订单号']
    settlement_type = int(row['修正后行方结算方式'])
    sql1_lines.append(
        f"UPDATE orders_detail_extra SET channel_settlement_type = {settlement_type}, "
        f"channel_settlement_time = supplier_settlement_time WHERE order_no = '{order_no}';"
    )

with open(OUTPUT_SHEET1, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql1_lines))
print(f"Sheet1 SQL 已生成: {OUTPUT_SHEET1} ({len(df1)} 条)")

# ---- Sheet2: 根据订单号更新行方结算类型 ----
sql2_lines = ["-- Sheet2: 根据集采单号更新 channel_settlement_type\n"]
for _, row in df2.iterrows():
    order_no = row['集采单号']
    settlement_type = int(row['修正后集采单行方结算方式'])
    sql2_lines.append(
        f"UPDATE orders_detail_extra SET channel_settlement_type = {settlement_type} "
        f"WHERE order_no = '{order_no}';"
    )

with open(OUTPUT_SHEET2, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql2_lines))
print(f"Sheet2 SQL 已生成: {OUTPUT_SHEET2} ({len(df2)} 条)")

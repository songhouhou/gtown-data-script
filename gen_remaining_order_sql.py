# -*- coding: utf-8 -*-
import pandas as pd
import os

INPUT = r"C:\Users\houhou.song\Downloads\剩余待修集采订单数据.xlsx"
if not os.path.exists(INPUT):
    INPUT = r"d:\PythonProjects\data-script\剩余待修集采订单数据.xlsx"

OUTPUT_SHEET1 = r"d:\PythonProjects\data-script\导出结果\sheet1_剩余待修集采订单_更新.sql"
OUTPUT_SHEET2 = r"d:\PythonProjects\data-script\导出结果\sheet2_剩余待修集采订单_更新.sql"

df1 = pd.read_excel(INPUT, sheet_name=0, dtype={'子订单号': str})
df2 = pd.read_excel(INPUT, sheet_name=1, dtype={'集采单号': str})

# ---- Sheet1: 更新 channel_settlement_type + channel_settlement_time + update_time ----
sql1 = ["-- Sheet1: 更新 channel_settlement_type, channel_settlement_time, update_time"]
for _, row in df1.iterrows():
    order_no = row['子订单号'].strip()
    stype = int(row['修正后行方结算方式'])
    stime = pd.to_datetime(row['修正后行方结算时间']).strftime('%Y-%m-%d %H:%M:%S')
    sql1.append(
        f"UPDATE orders_detail_extra SET channel_settlement_type = {stype}, "
        f"channel_settlement_time = '{stime}', update_time = NOW() "
        f"WHERE order_no = '{order_no}';"
    )

# ---- Sheet2: 更新 channel_settlement_type + update_time ----
sql2 = ["-- Sheet2: 更新 channel_settlement_type, update_time"]
for _, row in df2.iterrows():
    order_no = row['集采单号'].strip()
    stype = int(row['修正后集采单行方结算方式'])
    sql2.append(
        f"UPDATE orders_detail_extra SET channel_settlement_type = {stype}, "
        f"update_time = NOW() WHERE order_no = '{order_no}';"
    )

with open(OUTPUT_SHEET1, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql1))

with open(OUTPUT_SHEET2, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql2))

print(f"Sheet1 SQL 已生成: {OUTPUT_SHEET1} ({len(df1)} 条)")
print(f"Sheet2 SQL 已生成: {OUTPUT_SHEET2} ({len(df2)} 条)")

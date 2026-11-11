import pandas as pd
import os
from clickhouse_driver import connect

# 读取文件
excel_file = pd.ExcelFile('D:\海牙湾工作\权益订单刷行方结算时间\数据合并_20250717141912.xlsx')
df = excel_file.parse('Sheet1')

# 按每2000条数据进行分组
groups = [df['项目订单号'][i:i + 2000] for i in range(0, len(df), 2000)]

# ClickHouse 连接参数
clickhouse_config = {
    'host': 'cc-uf69bw1w26bz22155.public.clickhouse.ads.aliyuncs.com',
    'user': 'omp_select',
    'password': '3Lqcwr7s',
    'database': 'default'
}

# 存储有 channel_settlement_time 记录的项目订单号
has_channel_settlement_time = set()

# 遍历每个分组查询数据
for index, group in enumerate(groups):
    order_numbers = ', '.join(f"'{num}'" for num in group)

    try:
        print(f"开始查询第 {index + 1} 组的 channel_settlement_time 数据...")
        # 建立 ClickHouse 连接
        connection = connect(**clickhouse_config)
        cursor = connection.cursor()

        # 查询 channel_settlement_time 不为空的记录
        settlement_time_sql = f"""
        SELECT 
            o.channel_order_no
        FROM 
            ob_fms_order_sec_sql.orders o
        INNER JOIN 
            ob_fms_order_sec_sql.orders_detail_extra ode ON o.order_no = ode.order_no
        WHERE 
            o.channel_order_no IN ({order_numbers})
            AND ode.channel_settlement_time IS NOT NULL
            AND ode.is_del = 0; 
        """

        cursor.execute(settlement_time_sql)
        settlement_result = cursor.fetchall()

        # 提取有 channel_settlement_time 记录的项目订单号
        if settlement_result:
            # 直接从查询结果中提取订单号
            current_settlement_nos = [item[0] for item in settlement_result]
            has_channel_settlement_time.update(current_settlement_nos)
            print(f"第 {index + 1} 组查询完成，新增 {len(current_settlement_nos)} 个有行方结算时间的订单号")
        else:
            print(f"第 {index + 1} 组中无符合条件的记录")

        # 关闭连接
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"第 {index + 1} 组查询出错: {e}")

# 输出最终结果（不分组打印）
if has_channel_settlement_time:
    total = len(has_channel_settlement_time)
    print(f"\n===== 查询完成 =====")
    print(f"共找到 {total} 个存在行方结算时间的项目订单号：")
    # 直接打印所有订单号（用换行分隔，避免单行过长）
    for order_no in sorted(has_channel_settlement_time):
        print(order_no)
else:
    print("\n没有查询到任何存在行方结算时间的项目订单号")
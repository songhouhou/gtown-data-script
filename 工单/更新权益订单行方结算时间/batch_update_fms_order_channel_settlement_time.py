import pandas as pd
import os
from datetime import datetime
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

# 存储所有查询结果
all_results = []

# 遍历每个分组，生成 SQL 并查询数据
for index, group in enumerate(groups):
    order_numbers = ', '.join(f"'{num}'" for num in group)
    sql = f"""
    SELECT
      distinct channel_order_no,
      order_type
    FROM
      ob_fms_order_sec_sql.orders
    WHERE
      channel_order_no IN ({order_numbers});
    """

    # print(f"正在查询：{sql}")
    try:
        print(f"开始查询第 {index + 1} 组数据...")
        # 建立 ClickHouse 连接
        connection = connect(**clickhouse_config)
        cursor = connection.cursor()

        # 执行查询
        cursor.execute(sql)
        result = cursor.fetchall()

        # 将查询结果转换为 DataFrame 并添加到 all_results 列表中
        columns = [desc[0] for desc in cursor.description]
        result_df = pd.DataFrame(result, columns=columns)
        all_results.append(result_df)
        print(f"第 {index + 1} 组数据查询完成，查询到 {len(result_df)} 条记录。")

        # 找出没查询到的项目订单号
        queried_order_nos = set(result_df['channel_order_no']) if not result_df.empty else set()
        current_group_order_nos = set(group)
        not_found_order_nos = current_group_order_nos - queried_order_nos
        if not_found_order_nos:
            print(f"第 {index + 1} 组中未查询到的项目订单号: {not_found_order_nos}")
        else:
            print(f"第 {index + 1} 组的项目订单号全部查询到了")

        # 关闭连接
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"查询第 {index + 1} 组数据出错: {e}")

# 将所有查询结果合并为一个 DataFrame
if all_results:
    final_result = pd.concat(all_results, ignore_index=True)

    # 将结果保存为 Excel 文件
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = f'D:\海牙湾工作\权益订单刷行方结算时间\权益订单_订单类型_{timestamp}.xlsx'
    final_result.to_excel(output_file, index=False)
    print(f"所有查询完成，最终结果共 {len(final_result)} 条记录，已保存到 {output_file}。")

    # 生成并保存 SQL 更新语句
    print("开始生成批量 SQL 更新语句...")

    # 创建保存 SQL 文件的目录
    sql_dir = r'D:\海牙湾工作\权益订单刷行方结算时间'
    if not os.path.exists(sql_dir):
        os.makedirs(sql_dir)

    # 按订单类型分组，提取订单号列表
    type1_orders = final_result[final_result['order_type'] == 1]['channel_order_no'].tolist()
    type3_orders = final_result[final_result['order_type'] == 3]['channel_order_no'].tolist()
    other_types = final_result[~final_result['order_type'].isin([1, 3])][['order_type', 'channel_order_no']].values.tolist()

    # 批量生成 SQL（batch_size=1000）
    batch_size = 1000
    type1_sqls = []
    type3_sqls = []

    # 处理类型
    # 处理类型1的批量更新SQL
    for i in range(0, len(type1_orders), batch_size):
        batch_orders = type1_orders[i:i + batch_size]
        order_str = ", ".join(f"'{order}'" for order in batch_orders)
        print(f'批量更新类型1（第 {i//batch_size + 1} 批）：行方结算时间为卡密发送时间')
        # 批量更新SQL
        sql = f"""
UPDATE orders_detail_extra ode
INNER JOIN orders o ON ode.order_no = o.order_no
SET ode.channel_settlement_time = o.send_time
WHERE 
  o.channel_order_no IN ({order_str})  
  AND ode.channel_settlement_time IS NULL
  AND o.send_time IS NOT NULL;
        """
        type1_sqls.append(sql)

    # 处理类型3的批量更新SQL
    for i in range(0, len(type3_orders), batch_size):
        batch_orders = type3_orders[i:i + batch_size]
        order_str = ", ".join(f"'{order}'" for order in batch_orders)
        # 批量更新SQL
        print(f'-- 批量更新类型3（第 {i//batch_size + 1} 批）：行方结算时间为直充成功时间')
        sql = f"""
UPDATE orders_detail_extra ode
INNER JOIN orders o ON ode.order_no = o.order_no
SET ode.channel_settlement_time = o.update_time
WHERE 
  o.channel_order_no IN ({order_str})  
  AND ode.channel_settlement_time IS NULL
  AND o.update_time IS NOT NULL;
        """
        type3_sqls.append(sql)

    # 保存批量更新SQL到文件
    type1_sql_file = os.path.join(sql_dir, "权益订单_类型1_批量更新SQL.txt")
    type3_sql_file = os.path.join(sql_dir, "权益订单_类型3_批量更新SQL.txt")

    with open(type1_sql_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(type1_sqls))

    with open(type3_sql_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(type3_sqls))

    print(f"已生成批量更新SQL文件：")
    print(f"1. 类型1批量SQL（共 {len(type1_sqls)} 批）: {type1_sql_file}")
    print(f"2. 类型3批量SQL（共 {len(type3_sqls)} 批）: {type3_sql_file}")

    # 打印其他类型的订单信息
    if other_types:
        print("\n其他类型的订单信息：")
        for order_type, order_no in other_types:
            print(f"订单类型: {order_type}, 项目订单号: {order_no}")
    else:
        print("\n没有其他类型的订单。")
else:
    print("没有查询到任何结果。")
# import pandas as pd
# import os
# from datetime import datetime
# from clickhouse_driver import connect
#
# # 读取文件
# excel_file = pd.ExcelFile('D:\海牙湾工作\权益订单刷行方结算时间\数据合并_20250717141912.xlsx')
# df = excel_file.parse('Sheet1')
#
# # 按每2000条数据进行分组
# groups = [df['项目订单号'][i:i + 2000] for i in range(0, len(df), 2000)]
#
# # ClickHouse 连接参数
# clickhouse_config = {
#     'host': 'cc-uf69bw1w26bz22155.public.clickhouse.ads.aliyuncs.com',
#     'user': 'omp_select',
#     'password': '3Lqcwr7s',
#     'database': 'default'
# }
#
# # 存储所有查询结果
# all_results = []
#
# # 遍历每个分组，生成 SQL 并查询数据
# for index, group in enumerate(groups):
#     order_numbers = ', '.join(f"'{num}'" for num in group)
#     sql = f"""
#     SELECT
#       distinct channel_order_no,
#       order_type
#     FROM
#       ob_fms_order_sec_sql.orders
#     WHERE
#       channel_order_no IN ({order_numbers});
#     """
#
#     # print(f"正在查询：{sql}")
#     try:
#         print(f"开始查询第 {index + 1} 组数据...")
#         # 建立 ClickHouse 连接
#         connection = connect(**clickhouse_config)
#         cursor = connection.cursor()
#
#         # 执行查询
#         cursor.execute(sql)
#         result = cursor.fetchall()
#
#         # 将查询结果转换为 DataFrame 并添加到 all_results 列表中
#         columns = [desc[0] for desc in cursor.description]
#         result_df = pd.DataFrame(result, columns=columns)
#         all_results.append(result_df)
#         print(f"第 {index + 1} 组数据查询完成，查询到 {len(result_df)} 条记录。")
#
#         # 找出没查询到的项目订单号
#         queried_order_nos = set(result_df['channel_order_no']) if not result_df.empty else set()
#         current_group_order_nos = set(group)
#         not_found_order_nos = current_group_order_nos - queried_order_nos
#         if not_found_order_nos:
#             print(f"第 {index + 1} 组中未查询到的项目订单号: {not_found_order_nos}")
#         else:
#             print(f"第 {index + 1} 组的项目订单号全部查询到了")
#
#         # 关闭连接
#         cursor.close()
#         connection.close()
#     except Exception as e:
#         print(f"查询第 {index + 1} 组数据出错: {e}")
#
# # 将所有查询结果合并为一个 DataFrame
# if all_results:
#     final_result = pd.concat(all_results, ignore_index=True)
#
#     # 将结果保存为 Excel 文件
#     timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#     output_file = f'D:\海牙湾工作\权益订单刷行方结算时间\权益订单_订单类型_{timestamp}.xlsx'
#     final_result.to_excel(output_file, index=False)
#     print(f"所有查询完成，最终结果共 {len(final_result)} 条记录，已保存到 {output_file}。")
#
#     # 生成并保存 SQL 更新语句
#     print("开始生成 SQL 更新语句...")
#
#     # 创建保存 SQL 文件的目录
#     sql_dir = r'D:\海牙湾工作\权益订单刷行方结算时间'
#     if not os.path.exists(sql_dir):
#         os.makedirs(sql_dir)
#
#     # 初始化两种类型的 SQL 语句列表
#     type1_sqls = []
#     type3_sqls = []
#     other_types = []
#
#     # 遍历查询结果，生成对应的 SQL 更新语句
#     for _, row in final_result.iterrows():
#         channel_order_no = row['channel_order_no']
#         order_type = row['order_type']
#
#         if order_type == 1:
#             # 订单类型为 1 的 SQL 更新语句
#             # 更新行方结算时间为卡密发送时间
#             sql = f"""
# UPDATE orders_detail_extra ode
# INNER JOIN orders o ON ode.order_no = o.order_no
# SET ode.channel_settlement_time = o.send_time
# WHERE
#   o.channel_order_no = '{channel_order_no}'
#   AND ode.channel_settlement_time IS NULL
#   AND o.send_time IS NOT NULL;
#             """
#             type1_sqls.append(sql)
#         elif order_type == 3:
#             # 订单类型为 3 的 SQL 更新语句
#             # 更新行方结算时间为直充成功时间
#             sql = f"""
# UPDATE orders_detail_extra ode
# INNER JOIN orders o ON ode.order_no = o.order_no
# INNER JOIN orders_expand oe ON o.id = oe.id
# SET ode.channel_settlement_time = oe.supplier_update_time
# WHERE
#   o.channel_order_no = '{channel_order_no}'
#   AND ode.channel_settlement_time IS NULL
#   AND oe.supplier_update_time IS NOT NULL;
#             """
#             type3_sqls.append(sql)
#         else:
#             # 其他类型，记录类型和项目订单号
#             other_types.append(f"订单类型: {order_type}, 项目订单号: {channel_order_no}")
#
#     # 保存 SQL 语句到文件
#     type1_sql_file = os.path.join(sql_dir, "权益订单_类型1_更新SQL.txt")
#     type3_sql_file = os.path.join(sql_dir, "权益订单_类型3_更新SQL.txt")
#
#     with open(type1_sql_file, 'w', encoding='utf-8') as f:
#         f.write("\n".join(type1_sqls))
#
#     with open(type3_sql_file, 'w', encoding='utf-8') as f:
#         f.write("\n".join(type3_sqls))
#
#     print(f"已生成两种类型的 SQL 更新语句文件：")
#     print(f"1. 订单类型1的SQL: {type1_sql_file}")
#     print(f"2. 订单类型3的SQL: {type3_sql_file}")
#
#     # 打印其他类型的订单信息
#     if other_types:
#         print("\n其他类型的订单信息：")
#         for info in other_types:
#             print(info)
#     else:
#         print("\n没有其他类型的订单。")
# else:
#     print("没有查询到任何结果。")
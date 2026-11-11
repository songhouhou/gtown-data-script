import pandas as pd
import os
from datetime import datetime

# 指定文件夹路径
folder_path = 'D:\海牙湾工作\权益订单刷行方结算时间\源数据'

# 存储所有数据
all_data = []

# 获取文件夹下所有文件
files = os.listdir(folder_path)
total_files = sum(1 for file_name in files if file_name.endswith(('.xlsx', '.xls')))
processed_files = 0

# 遍历文件夹下的所有文件
for file_name in files:
    if file_name.endswith(('.xlsx', '.xls')):
        file_path = os.path.join(folder_path, file_name)
        try:
            processed_files += 1
            print(f'正在读取文件 {file_name} ({processed_files}/{total_files})...')
            # 读取文件
            excel_file = pd.ExcelFile(file_path)
            # 获取所有表名
            sheet_names = excel_file.sheet_names
            for sheet_name in sheet_names:
                df = excel_file.parse(sheet_name)
                all_data.append(df)
            print(f'文件 {file_name} 读取完成。')
        except Exception as e:
            print(f'读取文件 {file_name} 出错: {e}')

# 合并所有数据
if all_data:
    print('开始合并数据...')
    combined_data = pd.concat(all_data, ignore_index=True)
    print('数据合并完成。')

    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file_name = f'数据合并_{timestamp}.xlsx'
    output_file_path = os.path.join('D:\海牙湾工作\权益订单刷行方结算时间', output_file_name)

    # 保存合并后的数据
    print(f'正在将合并后的数据保存到 {output_file_name}...')
    combined_data.to_excel(output_file_path, index=False)
    print(f'数据已合并并保存到 {output_file_path}')
else:
    print('没有找到可合并的数据')
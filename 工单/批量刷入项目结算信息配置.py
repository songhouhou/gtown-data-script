# 批量刷入项目结算信息配置
# batch_update_project_payment_config
import pandas as pd
import os
from datetime import datetime

# 创建时间戳文件夹
timestamp_folder = datetime.now().strftime("%Y-%m-%d %H%M%S")
base_dir = '../项目结算信息配置'
output_dir = os.path.join(base_dir, timestamp_folder)

# 确保目录存在
os.makedirs(output_dir, exist_ok=True)

# 定义业务类型枚举
business_type_mapping = {
    '积分': 'YWLX000011',
    '商城业务': 'YWLX000012',
    '集采': 'YWLX000013',
    '代运营': 'YWLX000015',
    '权益业务': 'YWLX000020',
    '定制': 'YWLX000023',
    '分销': 'YWLX000025',
    '内部交易': 'YWLX000026',
    '企业购': 'YWLX000027'
}

# 定义对账条件枚举
check_account_condition_mapping = {
    '发货': 'DELIVER',
    '签收': 'SIGN'
}

# 定义对账周期枚举
check_account_cycle_mapping = {
    '周结': 'WEEK',
    '月结': 'MONTH',
    '双月结': 'TWOMONTHS',
    '季结': 'QUARTER'
}

# 定义收款条件枚举
receivable_condition_mapping = {
    '签收': 'SIGN',
    '发货': 'DELIVER',
    '对账': 'CHECKACCOUNT',
    '发票': 'INVOICE',
    '开票': 'INVOICE'
}

# 读取 Excel 文件
try:
    excel_file = pd.ExcelFile('D:\海牙湾工作\已确认项目中待刷信息3.xlsx')
except FileNotFoundError:
    print("错误：Excel 文件未找到，请检查文件路径是否正确。")
    exit(1)

# 获取第一个工作表中的数据
df = excel_file.parse(excel_file.sheet_names[0])

# 定义变量存储更新 SQL 语句和错误数据
project_sql = []
receivable_sql = []
prepayment_sql = []
error_data = []

# # 生成 project_info 表的更新语句
# for index, row in df.iterrows():
#     channel_code = row['项目编号']
#     business_type = row['业务类型']
#
#     if business_type in business_type_mapping:
#         business_type_code = business_type_mapping[business_type]
#         project_sql.append(f"UPDATE project_info SET business_type = '{business_type_code}', update_time = NOW() WHERE channel_code = '{channel_code}';")
#     else:
#         error_data.append(f"未知业务类型: 项目编号 {channel_code}, 业务类型 {business_type}")

# 生成 project_payment_config 表的更新语句
for index, row in df.iterrows():
    channel_code = row['项目编号']
    pay_type = row['收款方式']
    check_account_condition = row['对账条件']
    check_account_cycle = row['对账周期']

    # 处理对账周期x列
    if pd.notnull(row['对账周期x(每周x,每月x日,每2个月x日,每季第3月x日)']):
        check_account_cycle_days = str(int(row['对账周期x(每周x,每月x日,每2个月x日,每季第3月x日)']))
    else:
        check_account_cycle_days = None

    # 处理开票日列
    if pd.notnull(row['开票日(对账后x日)']):
        invoicing_days = str(int(row['开票日(对账后x日)']))
    else:
        invoicing_days = None

    receivable_condition = row['收款条件（发票=开票）'] if pd.notnull(row['收款条件（发票=开票）']) else None

    # 处理收款条件x列
    if pd.notnull(row['收款条件x(签收/发货/对账后x日)']):
        receivable_condition_days = str(int(row['收款条件x(签收/发货/对账后x日)']))
    else:
        receivable_condition_days = None

    receivable_period_days = row['收款日x(每周x[单选],每月x日[多选逗号分割],合同生效后x日)']
    # if pd.isnull(receivable_period_days):
    #     error_data.append(f"收款日x不能为空: 项目编号 {channel_code}")
    #     continue

    if pay_type == '预收款':
        if isinstance(receivable_period_days, str) and ',' in receivable_period_days:
            error_data.append(f"收款日包含逗号: 项目编号 {channel_code}, 收款日 {receivable_period_days}")

        if check_account_condition in check_account_condition_mapping:
            check_account_condition = check_account_condition_mapping[check_account_condition]
        else:
            error_data.append(f"未知对账条件: 项目编号 {channel_code}, 对账条件 {check_account_condition}")

        if check_account_cycle in check_account_cycle_mapping:
            check_account_cycle = check_account_cycle_mapping[check_account_cycle]
        else:
            error_data.append(f"未知对账周期: 项目编号 {channel_code}, 对账周期 {check_account_cycle}")

        # 构建预收款SQL语句
        sql_base = f"UPDATE project_payment_config SET pay_type = 1, check_account_condition = '{check_account_condition}', check_account_cycle = '{check_account_cycle}'"

        if check_account_cycle_days is not None:
            sql_base += f", check_account_cycle_days = '{check_account_cycle_days}'"
        if invoicing_days is not None:
            sql_base += f", invoicing_days = '{invoicing_days}'"

        # 只有当receivable_period_days不为空字符串时才添加该字段
        if str(receivable_period_days).lower() != 'nan' and receivable_period_days and str(receivable_period_days).strip() != '':
            sql_base += f", receivable_period_days = '{receivable_period_days}'"

        sql_base += ", update_time = NOW() WHERE channel_code = '{channel_code}';"
        prepayment_sql.append(sql_base.format(channel_code=channel_code))

    elif pay_type == '应收款':
        if check_account_condition in check_account_condition_mapping:
            check_account_condition = check_account_condition_mapping[check_account_condition]
        else:
            error_data.append(f"未知对账条件: 项目编号 {channel_code}, 对账条件 {check_account_condition}")

        if check_account_cycle in check_account_cycle_mapping:
            check_account_cycle = check_account_cycle_mapping[check_account_cycle]
        else:
            error_data.append(f"未知对账周期: 项目编号 {channel_code}, 对账周期 {check_account_cycle}")

        if receivable_condition in receivable_condition_mapping:
            receivable_condition = receivable_condition_mapping[receivable_condition]
        else:
            error_data.append(f"未知收款条件: 项目编号 {channel_code}, 收款条件 {receivable_condition}")

        # 构建应收款SQL语句
        sql_base = f"UPDATE project_payment_config SET pay_type = 2, check_account_condition = '{check_account_condition}', check_account_cycle = '{check_account_cycle}'"

        if check_account_cycle_days is not None:
            sql_base += f", check_account_cycle_days = '{check_account_cycle_days}'"
        if invoicing_days is not None:
            sql_base += f", invoicing_days = '{invoicing_days}'"
        if receivable_condition is not None:
            sql_base += f", receivable_condition = '{receivable_condition}'"
        if receivable_condition_days is not None:
            sql_base += f", receivable_condition_days = '{receivable_condition_days}'"

        # 只有当receivable_period_days不为空字符串时才添加该字段
        if str(receivable_period_days).lower() != 'nan' and receivable_period_days and str(receivable_period_days).strip() != '':
            sql_base += f", receivable_period_days = '{receivable_period_days}'"

        sql_base += ", update_time = NOW() WHERE channel_code = '{channel_code}';"
        receivable_sql.append(sql_base.format(channel_code=channel_code))
    else:
        error_data.append(f"未知收款方式: 项目编号 {channel_code}, 收款方式 {pay_type}")

# 将更新 SQL 语句写入不同文件
def write_sql_file(sql_list, filename):
    try:
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            for sql in sql_list:
                f.write(sql + '\n')
        print(f"已成功生成 {filename}")
    except Exception as e:
        print(f"生成 {filename} 时出错: {str(e)}")

# 写入SQL文件
# write_sql_file(project_sql, '项目SQL.sql')
write_sql_file(receivable_sql, '应收SQL.sql')
write_sql_file(prepayment_sql, '预收SQL.sql')

# 将错误数据写入文件
try:
    with open(os.path.join(output_dir, 'error_data.txt'), 'w', encoding='utf-8') as f:
        for error in error_data:
            f.write(error + '\n')
    print(f"已成功生成 error_data.txt")
except Exception as e:
    print(f"生成 error_data.txt 时出错: {str(e)}")

print(f"所有文件已生成到目录: {output_dir}")
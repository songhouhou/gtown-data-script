import clickhouse_connect
import csv
import time

# ===================== 【配置项】你只需要改这里 =====================
CK_HOST = "cc-uf69bw1w26bz22155.public.clickhouse.ads.aliyuncs.com"
CK_PORT = 8123
CK_USER = "omp_select"
CK_PASSWORD = "3Lqcwr7s"
CK_DATABASE = "ob_omp_product_sec_sql"

# 每批多少行（Excel 安全上限 100万）
BATCH_SIZE = 800000
# =================================================================

# 你的 SQL（已优化）
SQL = """
SELECT
    pfd.id AS `ID`,
    pfd.channel_code AS `渠道编码`,
    pfd.channel_name AS `渠道名称`,
    pfd.create_by AS `创建人`,
    pfd.create_time AS `创建时间`,
    pfd.update_by AS `更新人`,
    pfd.update_time AS `更新时间`,
    pfd.channel_finance_id AS `渠道财务ID`,
    pfd.order_detail_no AS `订单明细编号`,
    pfd.settlement_amount AS `结算金额`,
    pfd.settlement_already_verification_amount AS `结算已对账金额`,
    pfd.settlement_wait_verification_amount AS `结算待对账金额`,
    pfd.settlement_last_verification_amount AS `结算最后一次对账金额`,
    pfd.settlement_verification_status AS `结算对账状态`,
    pfd.already_verification_amount AS `已对账金额`,
    pfd.wait_verification_amount AS `待对账金额`,
    pfd.last_verification_amount AS `最后一次对账金额`,
    pfd.verification_status AS `对账状态`,
    pfd.verification_time AS `对账日期`,
    pfd.verification_batch AS `对账批次号`,
    pfd.invoice_no AS `发票号`,
    pfd.invoice_status AS `发票状态`,
    pfd.already_invoice_amount AS `已开票金额`,
    pfd.wait_invoice_amount AS `待开票金额`,
    pfd.returned_monty_no AS `回款号`,
    pfd.returned_monty_status AS `回款状态`,
    pfd.already_returned_monty AS `已回款金额`,
    pfd.wait_returned_monty AS `待回款金额`,
    pfd.is_del AS `是否删除`,
    pfd.invoice_time AS `开票日期`,
    pfd.returned_time AS `回款日期`,
    pfd.labour_verification_flag AS `凭证人工标识`,
    pfd.labour_invoice_flag AS `开票人工标识`,
    pfd.labour_returned_flag AS `回款人工标识`,
    pfd.refund_order AS `是否退货订单`,
    pfd.source_type AS `来源类型`,
    pfd.pay_amount AS `个人支付金额`,
    pfd.pay_already_verification_amount AS `个人支付已对账金额`,
    pfd.pay_wait_verification_amount AS `个人支付待对账金额`,
    pfd.pay_last_verification_amount AS `个人支付最后一次对账金额`,
    pfd.pay_verification_status AS `个人支付对账状态`,
    pfd.integral_amount AS `积分金额`,
    pfd.integral_already_verification_amount AS `积分已对账金额`,
    pfd.integral_wait_verification_amount AS `积分待对账金额`,
    pfd.integral_last_verification_amount AS `积分最后一次对账金额`,
    pfd.integral_verification_status AS `积分对账状态`,
    pfd.bank_discount_amount AS `渠道方补贴金额`,
    pfd.bank_discount_already_verification_amount AS `渠道方补贴已对账金额`,
    pfd.bank_discount_wait_verification_amount AS `渠道方补贴待对账金额`,
    pfd.bank_discount_last_verification_amount AS `渠道方补贴最后一次对账金额`,
    pfd.bank_discount_verification_status AS `渠道方补贴对账状态`,
    pfd.national_subsidy_amount AS `政府补贴-全国性金额`,
    pfd.national_subsidy_already_verification_amount AS `政府补贴-全国性已对账金额`,
    pfd.national_subsidy_wait_verification_amount AS `政府补贴-全国性待对账金额`,
    pfd.national_subsidy_last_verification_amount AS `政府补贴-全国性最后一次对账金额`,
    pfd.national_subsidy_verification_status AS `政府补贴-全国性对账状态`,
    pfd.city_subsidy_amount AS `政府补贴-地方性金额`,
    pfd.city_subsidy_already_verification_amount AS `政府补贴-地方性已对账金额`,
    pfd.city_subsidy_wait_verification_amount AS `政府补贴-地方性待对账金额`,
    pfd.city_subsidy_last_verification_amount AS `政府补贴-地方性最后一次对账金额`,
    pfd.city_subsidy_verification_status AS `政府补贴-地方性对账状态`,
    pfd.verification_type AS `对账类型：0-结算金额，1-非结算金额`,
    pfd.is_commission AS `是否计算佣金：0-不计算佣金，1-计算佣金`
FROM ob_omp_product_sec_sql.project_finance_details AS pfd
SEMI JOIN
(
    SELECT DISTINCT order_detail_no
    FROM ob_omp_order_sec_sql.order_profit_integration
    WHERE create_time >= '2026-01-01 00:00:00'
    AND is_del = 0
) AS opi
ON pfd.order_detail_no = opi.order_detail_no
"""

def export_ck_to_csv():
    start_time = time.time()
    print("正在连接 ClickHouse...")

    # 连接
    client = clickhouse_connect.get_client(
        host=CK_HOST,
        port=CK_PORT,
        user=CK_USER,
        password=CK_PASSWORD,
        database=CK_DATABASE
    )

    print("开始查询数据...")
    result = client.query(SQL)

    # 表头（中文别名）
    headers = [col[0] for col in result.column_names]

    file_no = 1
    row_count = 0

    # 创建第一个文件
    filename = f"项目财务数据_第{file_no}批.csv"
    f = open(filename, 'w', newline='', encoding='utf-8-sig')
    writer = csv.writer(f)
    writer.writerow(headers)

    print(f"开始写入第 {file_no} 个文件，每批 {BATCH_SIZE} 行...")

    # ✅ 修复这里：stream_rows() → rows
    for row in result.rows:
        writer.writerow(row)
        row_count += 1

        # 满80万行，切分文件
        if row_count % BATCH_SIZE == 0:
            f.close()
            print(f"✅ 已保存：{filename}")
            file_no += 1
            filename = f"项目财务数据_第{file_no}批.csv"
            f = open(filename, 'w', newline='', encoding='utf-8-sig')
            writer = csv.writer(f)
            writer.writerow(headers)

    f.close()
    print(f"✅ 已保存最后一个文件：{filename}")

    print(f"\n🎉 导出全部完成！")
    print(f"📊 总数据行数：{row_count}")
    print(f"⏱ 总耗时：{round(time.time() - start_time, 2)} 秒")

if __name__ == "__main__":
    export_ck_to_csv()
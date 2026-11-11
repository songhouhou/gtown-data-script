# 生成ck创建表语句
# get_ck_table_create_sql
# 该 Python 脚本用于批量调用指定 HTTP 接口
# 遍历预设的数据库表名列表
# 获取每个表对应的建表语句（CREATE TABLE），并将所有建表语句按规范格式整理后写入 TXT 文件，方便查看和使用。
import requests

# 定义请求头
headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://archery.g-town.com.cn',
        'priority': 'u=1, i',
        'referer': 'https://archery.g-town.com.cn/',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'x-csrftoken': 'c9hnjucRa4tLeVb9iHdh8ytgqn8UswCV',
        'x-requested-with': 'XMLHttpRequest',
        'Cookie': 'csrftoken=c9hnjucRa4tLeVb9iHdh8ytgqn8UswCV; sessionid=hqo07ctpm2ienqxebspyma19nyec0amh',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGFnIjoiNDc3OTA4Njk0NTk1NTI1MjYyNzg0ODI1MTQ5MTE4ODE1NjU4NDk2MzE5Mjc5Mjg3NDYxNDEwOTYwNzg3MDE0ODY3NjkwNzI3MDEyODMwOTQ5NDI2Nzk1NjY4NDk0ODYxMjYxODU0ODkxMDY1OTQ5Nzg0MDQ2NDg1NzIwODQxMTk0ODA5OTU1NDc5MzM1MDcxMTI4MTQ1MzgxNjQ5MjYyMTAxNTQ0OTk2NzY5NTQ4MzY2NzYzNTA5MjIzOTYyMzc0NjM3NDAzMTUzNDUzMjg5ODUyNzgyNzA3ODA1OTg1MDgzMzYzMjgzNTU4ODY0NzAyNzQ1NDM3MTk5MDQ4OTMyMTY5MjQ1MzY2NjMyNTQ1MzkwNDc4MjE3MzU3MzUzNTg2NDMxNTk3NzM5Njc4MTU3MjEzNDgyMDI0NjI3MzYzMzU5ODkxNjU5Mzc3NTYxNDY4NjQ5MDc4NjU0IiwidXNlcl9uYW1lIjoiYWRtaW4iLCJlbiI6ImFkbWluIiwiZW1wbG95ZWVJZCI6MywiY24iOiLnrqHnkIblkZgiLCJ1c2VySWQiOjMsImF1dGhvcml0aWVzIjpbXSwiY2xpZW50X2lkIjoiY2xpZW50SWQiLCJwaG9uZSI6IjEiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwidGVuYW50SWQiOjEwMDAwLCJkZXBhcnRtZW50IjoiLzEvIiwianRpIjoiNWZkODkzY2UtMDU2Ni00YTk3LWFkMTktNDJmMmJjYjM1MzAzIiwiZW1haWwiOiIxMjQxMjMxMkAxNjMuY29tIn0.hUquvDBOsJPcLfIGtpWfV1KhmrLDtYNzhdjN1esWvDAEej_fseJr2qqrBpYyg_d_FUeuIYYJxEYxoNEvp69cw6wYwtz8DBjWEByPUnaqJsvjdG3GRuTdrBh5_vdpjU2NkFxWcsMK-hBVNAvRouoBmLvJCi-gWpIIXJvX868xoCr3gYNNY4CumotyIPStHKhcMMQtQVrIXi4_rXNT39haLb95_H3aK6R_7MwhV7nSR0kIn37Ws6ZpuBqZ7T14pINLUARQiaUujKko9-V6viqrJ3xuaOXZUMUmWsxeEEHKY-06jjc_F3N_qNGmjCRbAIK2cXuopGN93pRAhfti8HlqKQ',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

# 定义请求URL
url = 'https://archery.g-town.com.cn/instance/describetable/'

# 定义需要查询的表名列表
table_names = [
        "account_balance",
        "account_flow",
        "account_warning_threshold",
        "active_area",
        "active_area_sku",
        "address",
        "apply_funds",
        "apply_funds_account_record",
        "arrival_notice",
        "arrival_notice_detail",
        "brand_operation_data",
        "card_config",
        "card_detail_config",
        "channel_item_group",
        "channel_item_price_record",
        "channel_item_subject_purchase_config",
        "channel_item_supplier",
        "channel_purchase_amount_detail",
        "channel_reminder_task",
        "common_warning",
        "common_warning_delay",
        "common_warning_relation",
        "contract_releve_agreement",
        "crm_project",
        "customer_business",
        "customer_business_follow_up_record",
        "customer_clue",
        "customer_clue_follow_up_record",
        "customer_contacts",
        "customer_contacts_care_record",
        "customer_distribution_record",
        "customer_info",
        "customer_primary",
        "customer_secondary",
        "customer_service_sms_log",
        "customer_service_sms_template",
        "file_info",
        "flyway_schema_history",
        "image_library",
        "invoice_info",
        "invoice_info_detail",
        "invoice_order_detail",
        "item_info",
        "item_supplier",
        "merchant_income_cost",
        "msg_group",
        "msg_group_relation",
        "msg_notify",
        "omp_api_config",
        "omp_audit_request",
        "omp_basic_category",
        "omp_basic_label",
        "omp_carrier",
        "omp_carrier_config",
        "omp_carrier_config_detail",
        "omp_carrier_config_dimension",
        "omp_channel",
        "omp_channel_business_properties",
        "omp_channel_payment_config",
        "omp_channel_product",
        "omp_channel_product_assess_fee",
        "omp_channel_product_attr",
        "omp_channel_product_autopush_config",
        "omp_channel_product_category",
        "omp_channel_product_contrast",
        "omp_channel_product_history_price_record",
        "omp_channel_product_price_record",
        "omp_channel_product_rate",
        "omp_channel_product_submit",
        "omp_channel_product_submit_channel",
        "omp_channel_update_log",
        "omp_customer",
        "omp_customer_business",
        "omp_customer_organization",
        "omp_customer_payment_config",
        "omp_customer_person",
        "omp_customer_primary",
        "omp_customer_sale",
        "omp_customer_secondary",
        "omp_dict",
        "omp_enterprise_subject",
        "omp_freight_template",
        "omp_freight_template_detail",
        "omp_freight_template_detail_fee",
        "omp_help_center_file",
        "omp_platform",
        "omp_premium",
        "omp_premium_sku",
        "omp_product_attr",
        "omp_product_attr_item",
        "omp_product_attr_name",
        "omp_product_attr_value",
        "omp_product_auto_submit",
        "omp_product_brand",
        "omp_product_brand_authorisation",
        "omp_product_brand_authorisation_relation",
        "omp_product_brand_trademark",
        "omp_product_brand_union",
        "omp_product_category",
        "omp_product_category_attr",
        "omp_product_category_parameter",
        "omp_product_category_weight",
        "omp_product_ccc_rebate",
        "omp_product_ccc_rebate_consume_log",
        "omp_product_config",
        "omp_product_purchase_config",
        "omp_product_rfq",
        "omp_product_rfq_item",
        "omp_product_rfq_supplier",
        "omp_product_sku",
        "omp_product_sku_attr",
        "omp_product_sku_consumption_tax",
        "omp_product_sku_group",
        "omp_product_sku_group_bak",
        "omp_product_sku_mask_config",
        "omp_product_sku_price_record",
        "omp_product_spu",
        "omp_product_spu_attr",
        "omp_product_spu_parameter",
        "omp_product_sync_log",
        "omp_product_sync_log_del",
        "omp_product_validity",
        "omp_project",
        "omp_project_detail",
        "omp_purchase_order",
        "omp_purchase_order_bak",
        "omp_purchase_order_bak_2020",
        "omp_purchase_order_details",
        "omp_purchase_order_details_bak",
        "omp_purchase_order_details_bak_2020",
        "omp_purchase_order_extra",
        "omp_purchase_order_extra_bak",
        "omp_purchase_order_payment",
        "omp_purchase_order_payment_batch",
        "omp_purchase_order_payment_batch_detail",
        "omp_purchase_order_payment_sku",
        "omp_purchase_order_payment_u8_record",
        "omp_purchase_order_refund",
        "omp_purchase_order_refund_details",
        "omp_purchase_order_refund_log",
        "omp_purchase_plan",
        "omp_purchase_rebate_record",
        "omp_purchase_rebate_rule",
        "omp_purchase_rebate_rule_detail",
        "omp_purchase_rebate_trace",
        "omp_purchase_receipt",
        "omp_purchase_receipt_details",
        "omp_purchase_receipt_draft",
        "omp_purchase_receipt_settlement_rel",
        "omp_requirement",
        "omp_requirement_details",
        "omp_requirement_purchase_order_mapping",
        "omp_rfq_quotation_round",
        "omp_sale_path_check",
        "omp_strategy_config",
        "omp_strategy_config_detail",
        "omp_supplier",
        "omp_supplier_balance",
        "omp_supplier_balance_detail",
        "omp_supplier_balance_payment",
        "omp_supplier_balance_payment_detail",
        "omp_supplier_category",
        "omp_supplier_config",
        "omp_supplier_contract",
        "omp_supplier_dimension_price",
        "omp_supplier_dimension_price_sku",
        "omp_supplier_product",
        "omp_supplier_product_focus",
        "omp_warehouse",
        "omp_wrapper",
        "oms_brand",
        "oms_category",
        "oms_channel",
        "oms_kaola_channel_config",
        "oms_order_detail_all",
        "oms_product_sku",
        "oms_product_spu",
        "op_sales_statistics_config",
        "package_material_info",
        "parameter",
        "payment_deduction",
        "payment_deduction_relation",
        "platform_mapping",
        "product_bk20201022",
        "product_history_record",
        "product_warehouse_config",
        "profit_report_rebate_config",
        "project_finance",
        "project_finance_bank",
        "project_finance_details",
        "project_finance_event",
        "project_finance_event_lines",
        "project_finance_relation",
        "project_finance_temp",
        "project_finance_voucher",
        "project_info",
        "project_info_extend",
        "project_info_invoice",
        "project_payment_config",
        "project_performance_target",
        "project_product",
        "project_product_config",
        "project_product_draft",
        "project_product_subsidy",
        "project_sku_demand_forecast",
        "project_sku_demand_forecast_history",
        "project_subsidy",
        "purchase_reconcile",
        "purchase_reconcile_detail",
        "purchase_requirements",
        "purchase_requirements_detail",
        "purchase_settlement",
        "purchase_settlement_detail",
        "recharge_record",
        "remote_freight_config",
        "remote_freight_config_detail",
        "remote_freight_config_sku",
        "restricted_inventory",
        "restricted_inventory_log",
        "scm_freight_template",
        "scm_freight_template_detail",
        "service_income_cost_config",
        "short_message_cost",
        "supplier",
        "supplier_address_info",
        "supplier_contact",
        "supplier_contract_agent_addr",
        "supplier_contract_agent_info",
        "supplier_contract_brand_item",
        "supplier_contract_info_item",
        "supplier_contract_price_info",
        "supplier_contract_rebate_item",
        "supplier_daily_evaluation",
        "supplier_evaluation_indicators",
        "supplier_evaluation_indicators_info",
        "supplier_evaluation_management",
        "supplier_evaluation_management_relation",
        "supplier_evaluation_results",
        "supplier_evaluation_results_item",
        "supplier_evaluation_template",
        "supplier_evaluation_template_weight",
        "supplier_invoice_log",
        "supplier_item",
        "supplier_item_batch_config",
        "supplier_item_mark_config",
        "supplier_level",
        "supplier_level_change_log",
        "supplier_notify_config",
        "supplier_payment",
        "supplier_product_price",
        "supplier_product_price_sku",
        "supplier_product_quotation",
        "supplier_product_quotation_item",
        "supplier_product_sku",
        "supplier_product_sku_online",
        "supplier_product_spu",
        "supplier_product_spu_attr",
        "supplier_sale_guarantee",
        "system_config",
        "tag_sku",
        "tax_code",
        "temp_activity_sku",
        "temp_category",
        "temp_employee",
        "temp_group_sku",
        "temp_group_sku_update",
        "temp_help_topic",
        "temp_jd_category",
        "temp_kaola_category",
        "temp_product_user1",
        "temp_sku",
        "temp_sku_property",
        "temp_spu_category",
        "temp_supplier_product",
        "temp_u8_sku",
        "third_filed_config",
        "tmp_channel",
        "tmp_channel_product",
        "tmp_channel_product1",
        "tmp_channel_product_rate",
        "tmp_sku_weight",
        "u8_user",
        "user_card",
        "warning_info"
    ]

def get_create_table_sql(table_name):
    """
    获取指定表的建表语句
    :param table_name: 表名
    :return: 建表语句，如果获取失败返回None
    """
    try:
        # 发送POST请求
        payload='instance_name=prod-clickhouse-uf69bw1w26bz22155-gtown&db_name=ob_omp_product_sec_sql&schema_name=&tb_name=' + table_name
        response = requests.request("POST", url, headers=headers, data=payload)
        # 检查响应状态码
        response.raise_for_status()
        # 解析JSON响应
        result = response.json()
        # print(result)

        # 提取建表语句
        if result.get('status') == 0 and result.get('data') and result['data'].get('rows'):
            # 建表语句在rows数组的第一个元素的第二个位置
            create_sql = result['data']['rows'][0][1]
            return create_sql
        else:
            print(f"获取表 {table_name} 的建表语句失败: {result.get('msg', '未知错误')}")
            return None
    except Exception as e:
        print(f"请求表 {table_name} 时发生异常: {str(e)}")
        return None

def save_sql_to_file(sql_content, filename='create_table_scripts.txt'):
    """
    将建表语句写入文件
    :param sql_content: 要写入的建表语句内容
    :param filename: 文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    print(f"建表语句已成功写入文件: {filename}")

def main():
    """
    主函数：遍历表名列表，获取建表语句并写入文件
    """
    # 存储所有建表语句
    all_create_sql = []

    # 遍历表名列表
    total_tables = len(table_names)
    for index, table_name in enumerate(table_names, 1):
        print(f"正在处理第 {index}/{total_tables} 个表: {table_name}")

        # 获取建表语句
        create_sql = get_create_table_sql(table_name)

        if create_sql:
            # 添加分隔符和表名标识，方便阅读
            # all_create_sql.append(f"========== 表名: {table_name} ==========\n")
            all_create_sql.append(create_sql)
            all_create_sql.append(";\n\n")  # 空行分隔
        else:
            all_create_sql.append(f"========== 表名: {table_name} ==========\n")
            all_create_sql.append("获取建表语句失败\n\n")

    # 将所有建表语句合并为一个字符串
    final_content = ''.join(all_create_sql)

    # 写入文件
    save_sql_to_file(final_content)

if __name__ == "__main__":
    # 安装依赖（如果未安装）
    # pip install requests

    # 执行主函数
    main()
from openpyxl import load_workbook

# ========== 1 姓名与产品经理ID映射 ==========
name_to_uid = {
    "宋祎斐": 11115,
    "闫小会": 11120,
    "徐振凯": 12058,
    "罗意": 12319,
    "张娴": 12345,
    "杜盼盼": 12981,
    "沈飞": 11774,
    "李萱雯": 12949
}

# ========== 2 读取文件路径 ==========
file_path = r"D:\PythonProjects\data-script\数据清洗-0609(1).xlsx"
wb = load_workbook(file_path)

# 存储sql列表
spu_update_sqls = []  # 更新omp_product_spu
sku_update_sqls = []  # 更新omp_product_sku

# ========== 第一块：更新商品经理sheet数据 ==========
ws_manager = wb["更新商品经理"]
# 跳过表头第一行，从第二行开始遍历
for row in ws_manager.iter_rows(min_row=2, values_only=True):
    spu_code = row[0]
    new_name = row[3]
    if not spu_code or not new_name:
        continue
    # 获取对应用户ID
    user_id = name_to_uid.get(new_name)
    if user_id is None:
        print(f"警告：未匹配到姓名 {new_name} spu:{spu_code} 跳过")
        continue
    # 拼接update spu sql
    sql = f"""UPDATE omp_product_spu SET product_user_id = {user_id}, product_user_name = '{new_name}', update_time = now() WHERE spu_code = '{spu_code}';"""
    spu_update_sqls.append(sql)

# ========== 第二块：更新商品激活状态sheet数据 ==========
ws_active = wb["更新商品激活状态"]
# 跳过表头
for row in ws_active.iter_rows(min_row=2, values_only=True):
    spu_code = row[0]
    sku_code = row[1]
    active_flag = row[3]
    if not sku_code or active_flag not in ["是", "否"]:
        continue
    # 是=1，否=0
    active_state = 1 if active_flag == "是" else 0
    # 拼接update sku sql
    sql = f"""UPDATE omp_product_sku SET active_state = {active_state}, update_time = now() WHERE sku_code = '{sku_code}';"""
    sku_update_sqls.append(sql)

# ========== 输出结果 ==========
print("=" * 50)
print(f"【SPU产品经理更新SQL 共{len(spu_update_sqls)}条】")
print("=" * 50)
for sql in spu_update_sqls:
    print(sql)

print("\n" + "=" * 50)
print(f"【SKU激活状态更新SQL 共{len(sku_update_sqls)}条】")
print("=" * 50)
for sql in sku_update_sqls:
    print(sql)

# ========== 可选：写入txt文件保存 ==========
with open("spu_update.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(spu_update_sqls))

with open("sku_active_update.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sku_update_sqls))

print("\nSQL已分别保存至 spu_update.sql / sku_active_update.sql")
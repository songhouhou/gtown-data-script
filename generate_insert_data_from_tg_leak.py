import re
from datetime import datetime


def parse_leak_txt(file_path: str, output_file: str = "output_leak.sql"):
    # 获取当前日期 yyyyMMdd，用于拼接表名
    today_str = datetime.now().strftime("%Y%m%d")
    table_name = f"leak_data_{today_str}"


def parse_leak_txt(file_path: str, ououtput_file: str = "output_leak.sql"):
    # 1. 读取全部文本
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. 正则拆分每组数据：匹配 第X组泄露
    group_pattern = re.compile(r"第\d+组泄露([\s\S]*?)(?=第\d+组泄露|$)")
    group_blocks = group_pattern.findall(content.strip())

    all_fields_raw = []
    group_data_list = []

    # 3. 解析每一组的 key: value，收集所有原始字段
    line_pattern = re.compile(r"[╭├╰]\s*(.+?)\s*:\s*(.+)")
    for block in group_blocks:
        data_row = {}
        lines = block.strip().splitlines()
        for line in lines:
            match = line_pattern.match(line.strip())
            if match:
                key = match.group(1).strip()
                val = match.group(2).strip()
                data_row[key] = val
                all_fields_raw.append(key)
        group_data_list.append(data_row)

    # ========== 核心修复：有序去重字段，保证无重复列 ==========
    field_list = list(dict.fromkeys(all_fields_raw))

    # 4. 生成CREATE TABLE语句（表名带日期后缀）
    create_sql_parts = []
    create_sql_parts.append(f"CREATE TABLE {table_name} (")
    create_sql_parts.append("    id INT AUTO_INCREMENT PRIMARY KEY,")

    # 字段类型判断
    for field in field_list:
        # 纯数字字段 1/2/3 设为BIGINT
        if re.fullmatch(r"\d+", field):
            col_def = f"    `{field}` BIGINT NULL,"
        # 包含日期格式值的字段设为DATETIME
        else:
            # 抽样判断该行是否存在日期格式值
            is_datetime = False
            for row in group_data_list:
                val = row.get(field, "")
                if re.match(r"\d{4}-\d{2}-\d{2}", val):
                    is_datetime = True
                    break
            if is_datetime:
                col_def = f"    `{field}` DATETIME NULL,"
            else:
                col_def = f"    `{field}` VARCHAR(2000) NULL,"
        create_sql_parts.append(col_def)

    # 移除最后一列末尾逗号，语法合规
    create_sql_parts[-1] = create_sql_parts[-1].rstrip(",")
    create_sql_parts.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    create_sql = "\n".join(create_sql_parts)

    # 5. 生成INSERT语句（自动适配带日期的新表名）
    insert_list = []
    field_wrap = ", ".join([f"`{f}`" for f in field_list])
    for row in group_data_list:
        val_list = []
        for f in field_list:
            raw_val = row.get(f, "NULL")
            if raw_val in ("NULL", "NUL"):
                val_list.append("NULL")
            else:
                # 转义单引号防止SQL语法错误
                escape_val = raw_val.replace("'", "''")
                val_list.append(f"'{escape_val}'")
        values_str = ", ".join(val_list)
        insert_sql = f"INSERT INTO {table_name} ({field_wrap}) VALUES ({values_str});"
        insert_list.append(insert_sql)

    # 6. 控制台打印SQL
    print(f"===== CREATE TABLE {table_name} 建表语句 =====")
    print(create_sql)
    print("\n===== INSERT 插入语句 =====")
    for sql in insert_list:
        print(sql)

    # 7. 写入SQL文件
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(f"===== CREATE TABLE {table_name} =====\n")
        out_f.write(create_sql + "\n\n")
        out_f.write("===== INSERT DATA =====\n")
        for sql in insert_list:
            out_f.write(sql + "\n")
    print(f"\nSQL已自动保存到 {output_file} 文件")
    print(f"生成数据表名：{table_name}")


if __name__ == "__main__":
    # 修改这里为你的txt文件路径
    TXT_FILE_PATH = r"C:\Users\houhou.song\Downloads\result.txt"
    OUT_PUT_SQL_FILE_PATH = r"C:\Users\houhou.song\Downloads\output_leak.sql"
    parse_leak_txt(TXT_FILE_PATH, OUT_PUT_SQL_FILE_PATH)

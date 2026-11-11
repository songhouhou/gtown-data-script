# 将大型CSV文件按指定行数拆分成多个小文件
# split_csv_into_small_files
import csv
import os
from typing import Optional

def split_csv_by_rows(
        input_file: str,
        output_dir: str = "split_files",
        rows_per_file: int = 600000,
        encoding: str = "utf-8",
        delimiter: str = ",",
        quotechar: str = '"'
) -> None:
    """
    将大型CSV文件按指定行数拆分成多个小文件

    Args:
        input_file: 输入CSV文件的路径
        output_dir: 拆分后文件的输出目录（默认：split_files）
        rows_per_file: 每个拆分文件的行数（默认：600000）
        encoding: 文件编码（默认：utf-8）
        delimiter: CSV分隔符（默认：,）
        quotechar: CSV引用符（默认："）

    Raises:
        FileNotFoundError: 如果输入文件不存在
        ValueError: 如果输入文件不是CSV格式或行数设置无效
    """
    # 验证输入文件
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"输入文件不存在：{input_file}")

    if not input_file.lower().endswith(".csv"):
        raise ValueError(f"输入文件不是CSV格式：{input_file}")

    if rows_per_file <= 0:
        raise ValueError(f"行数必须大于0，当前值：{rows_per_file}")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 获取输入文件名（不含路径和扩展名）
    file_name = os.path.splitext(os.path.basename(input_file))[0]

    # 初始化变量
    file_counter = 1  # 拆分文件计数器
    current_row_count = 0  # 当前文件已写入行数
    output_file: Optional[csv.writer] = None
    output_handle = None

    try:
        # 打开输入CSV文件
        with open(input_file, "r", encoding=encoding, newline="") as infile:
            reader = csv.reader(infile, delimiter=delimiter, quotechar=quotechar)

            # 读取表头（第一行）
            header = next(reader)

            # 遍历CSV数据行
            for row in reader:
                # 如果是新文件或当前文件已达行数限制，创建新文件
                if current_row_count == 0:
                    # 关闭上一个文件句柄
                    if output_handle:
                        output_handle.close()

                    # 构建新文件路径
                    output_file_path = os.path.join(
                        output_dir,
                        f"{file_name}_part_{file_counter:03d}.csv"
                    )

                    # 打开新文件并写入表头
                    output_handle = open(output_file_path, "w", encoding=encoding, newline="")
                    output_file = csv.writer(output_handle, delimiter=delimiter, quotechar=quotechar)
                    output_file.writerow(header)

                    print(f"创建拆分文件：{output_file_path}")

                # 写入数据行
                output_file.writerow(row)
                current_row_count += 1

                # 如果达到行数限制，重置计数器并递增文件编号
                if current_row_count >= rows_per_file:
                    current_row_count = 0
                    file_counter += 1

        # 处理最后一个文件（如果有剩余行）
        if output_handle:
            output_handle.close()

        print(f"\n拆分完成！总共生成 {file_counter - 1} 个文件")
        print(f"输出目录：{os.path.abspath(output_dir)}")

    except Exception as e:
        # 确保文件句柄被关闭
        if output_handle:
            output_handle.close()
        raise RuntimeError(f"拆分CSV文件时出错：{str(e)}") from e

# 主函数：方便直接运行
if __name__ == "__main__":
    # ========== 配置参数 ==========
    # CSV文件路径
    INPUT_CSV_PATH = "../导出结果/data_export_fms_order_sec_2026_01_07_16_53_37.csv"
    # 每文件60万行
    ROWS_PER_FILE = 700000
    OUTPUT_DIRECTORY = "split_csv_files"  # 输出目录名
    FILE_ENCODING = "utf-8"  # 文件编码（如果是GBK格式请改为gbk）

    # 执行拆分
    try:
        split_csv_by_rows(
            input_file=INPUT_CSV_PATH,
            output_dir=OUTPUT_DIRECTORY,
            rows_per_file=ROWS_PER_FILE,
            encoding=FILE_ENCODING
        )
    except Exception as e:
        print(f"错误：{e}")
# 找出TXT文件重复的行
# find_duplicate_line_from_txt
def find_duplicates_in_txt(file_path: str) -> set:
    """
    读取TXT文件，找出其中重复的行内容
    :param file_path: TXT文件路径
    :return: 包含所有重复行内容的集合
    """
    # 存储所有已读取的行
    all_lines = set()
    # 存储重复的行（去重后的）
    duplicate_lines = set()

    try:
        # 打开文件并逐行读取
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, start=1):
                # 去除行首尾的空白字符（换行、空格、制表符等），根据需求可调整
                clean_line = line.strip()
                # 跳过空行（可选，根据你的需求决定是否保留）
                if not clean_line:
                    continue

                # 判断当前行是否已存在
                if clean_line in all_lines:
                    # 已存在则加入重复集合
                    duplicate_lines.add(clean_line)
                    print(f"⚠️  第{line_num}行发现重复内容：{clean_line}")
                else:
                    # 不存在则加入已读取集合
                    all_lines.add(clean_line)

        # 输出最终结果
        if duplicate_lines:
            print(f"\n📊 总计发现 {len(duplicate_lines)} 种重复内容：")
            for dup_line in duplicate_lines:
                print(f"   - {dup_line}")
        else:
            print("\n✅ 文件中未发现任何重复内容")

        return duplicate_lines

    except FileNotFoundError:
        print(f"❌ 错误：未找到文件 {file_path}")
        return set()
    except Exception as e:
        print(f"❌ 读取文件时发生错误：{str(e)}")
        return set()

# 调用示例
if __name__ == "__main__":
    # 替换为你的TXT文件路径
    txt_file_path = "../temp.txt"
    duplicates = find_duplicates_in_txt(txt_file_path)
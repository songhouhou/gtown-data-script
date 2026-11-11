import csv
import json
import sqlite3
from pathlib import Path


class SQLiteDb3Reader:
    def __init__(self, db_file_path: str):
        self.db_path = Path(db_file_path)
        self.conn = None
        self.cursor = None
        # 连接数据库
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
        self.conn = sqlite3.connect(str(self.db_path))
        # 查询返回字典格式（字段名:值），更方便处理
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print(f"✅ 成功连接数据库：{self.db_path.name}")

    def get_all_tables(self) -> list:
        """获取数据库内所有表名"""
        sql = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        self.cursor.execute(sql)
        tables = [row["name"] for row in self.cursor.fetchall()]
        return tables

    def query_table_all(self, table_name: str) -> list[dict]:
        """读取整张表所有数据，返回字典列表"""
        self.cursor.execute(f"SELECT * FROM {table_name};")
        rows = self.cursor.fetchall()
        result = [dict(row) for row in rows]
        return result

    def query_custom_sql(self, sql: str, params: tuple = ()) -> list[dict]:
        """执行自定义SQL，支持防注入参数"""
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def export_to_json(self, table_name: str, save_json_path: str):
        """将单表数据导出为JSON文件"""
        data = self.query_table_all(table_name)
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📄 表 {table_name} 已导出至 {save_json_path}")

    def export_to_csv(self, table_name: str, save_csv_path: str):
        """将单表数据导出为CSV表格"""
        data = self.query_table_all(table_name)
        if not data:
            print(f"表 {table_name} 无数据，跳过导出")
            return
        # 表头取第一条数据的key
        headers = list(data[0].keys())
        with open(save_csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"📊 表 {table_name} 已导出至 {save_csv_path}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("🔌 数据库连接已关闭")


if __name__ == "__main__":
    # ========== db3文件所在目录 ==========
    DB_FOLDER = r"C:\Users\houhou.song\AppData\Local\ShadowBot"
    # =======================================
    import glob

    # 递归查找所有子目录下的.db3
    db3_files = glob.glob(f"{DB_FOLDER}/**/*.db3", recursive=True)
    if not db3_files:
        print("目录下未找到任何.db3数据库文件")
        exit()

    print(f"共找到 {len(db3_files)} 个.db3数据库文件：")
    print(*db3_files, sep="\n")
    for DB_FILE in db3_files:
        print(f"\n==================== 开始读取数据库：{DB_FILE} ====================")
        try:
            db_reader = SQLiteDb3Reader(DB_FILE)

            # 1. 打印所有数据表
            table_list = db_reader.get_all_tables()
            print("\n=== 当前库所有数据表 ===")
            for t in table_list:
                print("-", t)

            if table_list:
                # 遍历每一张表，输出全部数据
                for target_table in table_list:
                    print(f"\n==================== 数据表：{target_table} ====================")
                    table_data = db_reader.query_table_all(target_table)
                    if not table_data:
                        print(f"表 {target_table} 无任何数据")
                        continue
                    for row in table_data:
                        print(row)

            db_reader.close()
        except Exception as e:
            print(f"❌ 读取 {DB_FILE} 失败：{str(e)}")
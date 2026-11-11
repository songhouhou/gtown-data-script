import os
import re
import csv
import smtplib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from email.mime.text import MIMEText
from email.header import Header
import pandas as pd

# ====================== 配置项（自行修改）======================
# 发件邮箱配置
SENDER_EMAIL = "你的发件邮箱@qq.com"
SENDER_AUTH_CODE = "邮箱授权码"  # 不是登录密码
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# 发送记录存储路径
LOG_DIR = r"D:\卡密发送记录"
LOG_FILE = os.path.join(LOG_DIR, "send_log.csv")

# 邮箱正则校验
EMAIL_REG = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
# Excel 规定表头
NEED_HEADERS = ["商品名称", "卡号", "卡密", "收件邮箱"]
# =================================================================

class CardEmailSender:
    def __init__(self, root):
        self.root = root
        self.root.title("卡密批量邮件发送工具")
        self.root.geometry("750x500")

        # 变量
        self.excel_path = ""
        self.df = None
        self.sent_record = set()  # 已发送卡号卡密集合

        # 初始化日志目录&加载历史记录
        self.init_log()

        # 界面布局
        self.create_widgets()

    def init_log(self):
        """初始化日志目录 + 加载已发送记录"""
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        # 读取历史发送记录
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        key = f"{row['卡号']}_{row['卡密']}"
                        self.sent_record.add(key)
            except Exception:
                self.log("警告：历史记录文件读取异常，将重新记录")

    def create_widgets(self):
        """搭建UI界面"""
        # 1. 固定接收人
        tk.Label(self.root, text="固定接收人(多邮箱英文逗号分隔)：").place(x=20, y=20)
        self.fixed_email_var = tk.StringVar()
        self.fixed_email_var.set("cadeo.xie@g-town.com.cn")
        tk.Entry(self.root, textvariable=self.fixed_email_var, width=60).place(x=220, y=22)

        # 2. 文件选择
        tk.Label(self.root, text="选择Excel文件：").place(x=20, y=60)
        self.file_path_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.file_path_var, width=60, state="readonly").place(x=120, y=62)
        tk.Button(self.root, text="上传文件", command=self.select_file, width=10).place(x=600, y=60)

        # 3. 功能按钮
        tk.Button(self.root, text="开始发送", command=self.start_send, bg="#4CAF50", fg="white", width=12).place(x=200, y=100)
        tk.Button(self.root, text="清空日志", command=self.clear_log, width=10).place(x=350, y=100)

        # 4. 日志输出框
        tk.Label(self.root, text="运行日志：").place(x=20, y=140)
        self.log_text = scrolledtext.ScrolledText(self.root, width=90, height=18)
        self.log_text.place(x=20, y=165)

    def log(self, msg):
        """日志输出"""
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def check_email_format(self, email):
        """校验单个邮箱格式"""
        return bool(EMAIL_REG.match(email.strip()))

    def select_file(self):
        """选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="请选择Excel文件",
            filetypes=[("Excel 文件", "*.xlsx;*.xls"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        # 校验文件后缀
        if not file_path.endswith((".xlsx", ".xls")):
            messagebox.showerror("错误", "请选择 .xlsx / .xls 格式的Excel文件！")
            self.log("错误：上传文件非Excel格式")
            return
        self.excel_path = file_path
        self.file_path_var.set(file_path)
        self.log(f"已选择文件：{file_path}")
        # 预加载数据
        self.load_excel()

    def load_excel(self):
        """读取并校验Excel数据"""
        try:
            self.df = pd.read_excel(self.excel_path)
        except Exception as e:
            messagebox.showerror("读取失败", f"Excel读取异常：{str(e)}")
            self.log(f"错误：Excel读取失败 -> {str(e)}")
            self.df = None
            return

        # 校验表头
        if not all(h in self.df.columns for h in NEED_HEADERS):
            err = f"表头错误！必须包含：{','.join(NEED_HEADERS)}"
            messagebox.showerror("表头错误", err)
            self.log(err)
            self.df = None
            return
        self.log("✅ Excel表头校验通过")

        # 逐行校验空值 + 邮箱格式
        error_list = []
        for idx, row in self.df.iterrows():
            row_num = idx + 2  # Excel行号(表头1行)
            name = str(row["商品名称"]).strip()
            card_no = str(row["卡号"]).strip()
            card_pwd = str(row["卡密"]).strip()
            to_email = str(row["收件邮箱"]).strip()

            # 空值校验
            if not all([name, card_no, card_pwd, to_email]):
                error_list.append(f"第{row_num}行：存在空数据")
                continue
            # 收件邮箱格式
            if not self.check_email_format(to_email):
                error_list.append(f"第{row_num}行：收件邮箱【{to_email}】格式错误")

        # 校验固定接收人
        fixed_emails = [e.strip() for e in self.fixed_email_var.get().split(",") if e.strip()]
        for fe in fixed_emails:
            if not self.check_email_format(fe):
                error_list.append(f"固定接收人【{fe}】格式错误")

        if error_list:
            err_msg = "\n".join(error_list)
            messagebox.showerror("数据校验失败", err_msg)
            self.log("❌ 数据校验不通过：\n" + err_msg)
            self.df = None
            return

        self.log("✅ 所有数据、邮箱格式校验通过")

    def group_data(self):
        """按收件邮箱合并数据"""
        group_dict = {}
        for _, row in self.df.iterrows():
            to_email = row["收件邮箱"].strip()
            info = f"商品：{row['商品名称']}，卡号：{row['卡号']}，卡密：{row['卡密']}"
            if to_email not in group_dict:
                group_dict[to_email] = []
            group_dict[to_email].append(info)
        return group_dict

    def write_log(self, row_data):
        """写入发送记录到CSV"""
        try:
            with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=NEED_HEADERS)
                # 新文件则写入表头
                if os.path.getsize(LOG_FILE) == 0:
                    writer.writeheader()
                writer.writerow(row_data)
        except Exception as e:
            self.log(f"警告：记录写入失败 -> {str(e)}")

    def send_mail(self, to_list, content):
        """发送邮件"""
        try:
            msg = MIMEText(content, "plain", "utf-8")
            msg["From"] = Header(f"卡密发放工具<{SENDER_EMAIL}>", "utf-8")
            msg["Subject"] = Header("卡密发放通知", "utf-8")

            # SSL发送
            smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            smtp.login(SENDER_EMAIL, SENDER_AUTH_CODE)
            smtp.sendmail(SENDER_EMAIL, to_list, msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            self.log(f"邮件发送异常：{str(e)}")
            return False

    def start_send(self):
        """主发送逻辑"""
        if not self.df:
            messagebox.showwarning("提示", "请先上传并校验Excel文件！")
            return

        # 解析固定接收人
        fixed_emails = [e.strip() for e in self.fixed_email_var.get().split(",") if e.strip()]
        group_data = self.group_data()
        total = len(group_data)
        success = 0

        for target_email, content_list in group_data.items():
            # 合并邮件内容
            mail_content = "\n".join(content_list)
            # 合并收件人：当前邮箱 + 固定接收人
            all_receiver = [target_email] + fixed_emails
            self.log(f"正在发送至：{target_email}")

            # 先判断是否有重复卡密
            repeat_flag = False
            for _, row in self.df.iterrows():
                key = f"{row['卡号']}_{row['卡密']}"
                if key in self.sent_record:
                    repeat_flag = True
                    break
            if repeat_flag:
                self.log(f"❌ {target_email} 包含已发送卡密，跳过")
                continue

            # 执行发送
            if self.send_mail(all_receiver, mail_content):
                self.log(f"✅ {target_email} 发送成功")
                success += 1
                # 写入记录 & 更新内存集合
                for _, row in self.df.iterrows():
                    row_dict = {k: row[k] for k in NEED_HEADERS}
                    self.write_log(row_dict)
                    key = f"{row['卡号']}_{row['卡密']}"
                    self.sent_record.add(key)
            else:
                self.log(f"❌ {target_email} 发送失败")

        self.log(f"\n===== 发送完成 =====")
        self.log(f"总计待发送邮箱：{total} 个，成功：{success} 个")
        messagebox.showinfo("完成", f"发送结束！\n总计：{total} 封\n成功：{success} 封")

if __name__ == "__main__":
    root = tk.Tk()
    app = CardEmailSender(root)
    root.mainloop()
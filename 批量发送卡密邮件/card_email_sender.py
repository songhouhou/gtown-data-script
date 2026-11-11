# 卡密批量邮件发送工具
# 功能：批量读取Excel内卡密数据，按邮箱合并发送邮件，支持重复发送拦截
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import re
import os
import csv
from datetime import datetime

# ================ 全局配置区 ================
# 发送记录配置
SEND_LOG_DIR = r"D:\卡密发送记录"
SEND_LOG_FILE = os.path.join(SEND_LOG_DIR, "send_log.csv")
REQUIRED_HEADERS = ["商品名称", "卡号", "卡密", "收件邮箱"]

# 邮箱正则表达式
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# ================ SMTP邮箱配置 ================
# 邮件服务器的SMTP地址
SMTP_HOST = "smtp.mxhichina.com"
# 邮件服务器的SMTP端口
SMTP_PORT = 465
# 发件人邮箱
SMTP_FROM = "BosExchange@g-town.com.cn"
# 用户名（通常与发件人邮箱相同）
SMTP_USER = "BosExchange@g-town.com.cn"
# 密码/授权码
SMTP_PASSWORD = "Public321"
# 使用SSL安全连接
SMTP_SSL_ENABLE = True
# 使用STARTTLS安全连接（与SSL二选一）
SMTP_STARTTLS_ENABLE = False

# ================ 固定接收人配置 ================
# 固定抄送/收件人，多个邮箱用英文逗号分隔
# test
FIXED_RECIPIENTS = "cadeo.xie@g-town.com.cn,zheng.zhao@g-town.com.cn"
# prod
# FIXED_RECIPIENTS = "baoyi.li@g-town.com.cn,michelle.kang@g-town.com.cn,vincy.wang@g-town.com.cn"

# ================ 发送配置 ================
# 发送邮件间隔时间（秒），避免发送过快被服务器限流
SEND_INTERVAL = 0.2

class CardEmailSender:
    def __init__(self, root):
        self.root = root
        self.root.title("卡密批量邮件发送工具 By Double hou")
        self.root.geometry("900x700")
        
        # 初始化变量
        self.excel_data = None
        # 从全局配置读取固定接收人默认值
        self.fixed_recipients = tk.StringVar(value=FIXED_RECIPIENTS)
        
        # 创建界面
        self.create_widgets()
        
        # 确保日志目录存在
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """确保发送记录目录存在"""
        if not os.path.exists(SEND_LOG_DIR):
            os.makedirs(SEND_LOG_DIR)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件上传区域
        file_frame = ttk.LabelFrame(main_frame, text="文件上传", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=60, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="选择Excel文件", command=self.select_file).pack(side=tk.LEFT)
        
        # 固定接收人区域
        recipient_frame = ttk.LabelFrame(main_frame, text="固定抄送/收件人", padding="10")
        recipient_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(recipient_frame, text="多个邮箱用英文逗号分隔:").pack(side=tk.LEFT)
        ttk.Entry(recipient_frame, textvariable=self.fixed_recipients, width=60).pack(side=tk.LEFT, padx=5)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="开始发送", command=self.start_send).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空内容", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # 日志展示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        # 同时输出到控制台
        print(log_line.strip())
    
    def select_file(self):
        """选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx;*.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 检查文件扩展名
            if not (file_path.endswith(".xlsx") or file_path.endswith(".xls")):
                messagebox.showerror("错误", "请选择有效的Excel文件（.xlsx或.xls格式）")
                return
            
            self.file_path.set(file_path)
            self.log(f"已选择文件: {file_path}")
    
    def validate_email(self, email):
        """校验邮箱格式"""
        return bool(EMAIL_REGEX.match(email.strip()))
    
    def validate_excel_headers(self, df):
        """校验Excel表头"""
        headers = df.columns.tolist()
        for required in REQUIRED_HEADERS:
            if required not in headers:
                return False, f"缺失必需表头: {required}"
        return True, ""
    
    def validate_data(self, df):
        """校验数据完整性"""
        errors = []
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel行号（从2开始，因为1是表头）
            
            # 检查空值
            if pd.isna(row["商品名称"]) or str(row["商品名称"]).strip() == "":
                errors.append(f"第{row_num}行: 商品名称为空")
            
            if pd.isna(row["卡号"]) or str(row["卡号"]).strip() == "":
                errors.append(f"第{row_num}行: 卡号为空")
            
            if pd.isna(row["卡密"]) or str(row["卡密"]).strip() == "":
                errors.append(f"第{row_num}行: 卡密为空")
            
            if pd.isna(row["收件邮箱"]) or str(row["收件邮箱"]).strip() == "":
                errors.append(f"第{row_num}行: 收件邮箱为空")
            else:
                # 校验邮箱格式
                email = str(row["收件邮箱"]).strip()
                if not self.validate_email(email):
                    errors.append(f"第{row_num}行: 邮箱格式错误 - {email}")
        
        return errors
    
    def validate_fixed_recipients(self):
        """校验固定接收人邮箱"""
        recipients = self.fixed_recipients.get().strip()
        if not recipients:
            return []
        
        errors = []
        for email in recipients.split(","):
            email = email.strip()
            if email and not self.validate_email(email):
                errors.append(f"固定接收人邮箱格式错误: {email}")
        
        return errors
    
    def load_excel(self):
        """加载并校验Excel文件"""
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择Excel文件")
            return None
        
        try:
            # 读取Excel文件
            if file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path, engine="openpyxl")
            else:
                df = pd.read_excel(file_path, engine="xlrd")
            
            self.log(f"成功读取Excel文件，共 {len(df)} 行数据")
            
            # 打印数据行
            self.log("--- 数据内容 ---")
            for index, row in df.iterrows():
                row_num = index + 2
                self.log(f"第{row_num}行: 商品名称={row['商品名称']}, 卡号={row['卡号']}, 卡密={row['卡密']}, 收件邮箱={row['收件邮箱']}")
            self.log("--- 数据内容结束 ---")
            
            # 校验表头
            valid, msg = self.validate_excel_headers(df)
            if not valid:
                self.log(msg, "ERROR")
                messagebox.showerror("错误", msg)
                return None
            
            self.log("表头校验通过")
            
            # 校验数据
            errors = self.validate_data(df)
            if errors:
                error_msg = "\n".join(errors)
                self.log(f"数据校验失败:\n{error_msg}", "ERROR")
                messagebox.showerror("数据校验失败", error_msg)
                return None
            
            self.log("数据校验通过")
            
            return df
        
        except Exception as e:
            error_msg = f"读取Excel文件失败: {str(e)}"
            self.log(error_msg, "ERROR")
            messagebox.showerror("错误", error_msg)
            return None
    
    def load_sent_records(self):
        """加载已发送记录"""
        records = set()
        
        if os.path.exists(SEND_LOG_FILE):
            try:
                with open(SEND_LOG_FILE, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        card_key = (row.get("卡号", ""), row.get("卡密", ""))
                        if card_key[0] and card_key[1]:
                            records.add(card_key)
                self.log(f"已加载 {len(records)} 条发送记录")
            except Exception as e:
                self.log(f"加载发送记录失败: {str(e)}", "WARNING")
        
        return records
    
    def check_duplicate(self, df):
        """检查重复发送"""
        records = self.load_sent_records()
        duplicates = []
        
        for index, row in df.iterrows():
            row_num = index + 2
            card_no = str(row["卡号"]).strip()
            card_pwd = str(row["卡密"]).strip()
            card_key = (card_no, card_pwd)
            
            if card_key in records:
                duplicates.append(f"第{row_num}行: 卡号[{card_no}]卡密已发送过")
        
        return duplicates
    
    def merge_by_email(self, df):
        """按邮箱合并数据"""
        email_groups = {}
        
        for _, row in df.iterrows():
            email = str(row["收件邮箱"]).strip()
            if email not in email_groups:
                email_groups[email] = []
            
            email_groups[email].append({
                "商品名称": str(row["商品名称"]).strip(),
                "卡号": str(row["卡号"]).strip(),
                "卡密": str(row["卡密"]).strip()
            })
        
        # 打印合并后的结果
        self.log(f"合并完成，共 {len(email_groups)} 个收件邮箱")
        self.log("--- 合并结果 ---")
        for idx, (email, cards) in enumerate(email_groups.items(), 1):
            self.log(f"邮箱{idx}: {email}")
            for card_idx, card in enumerate(cards, 1):
                self.log(f"  卡密{card_idx}: 商品名称={card['商品名称']}, 卡号={card['卡号']}, 卡密={card['卡密']}")
        self.log("--- 合并结果结束 ---")
        
        return email_groups
    
    def send_email(self, to_email, card_list, fixed_recipients):
        """发送单封邮件"""
        # 构建邮件内容
        content = "<html><body>"
        content += "<p>你好，</p>"
        content += "<p>&nbsp;</p>"
        
        # 添加卡密信息
        for card in card_list:
            content += f"<p>辛苦查收【{card['商品名称']}】，卡号为【{card['卡号']}】，卡密为：【{card['卡密']}】，谢谢</p>"
        
        content += "<p>&nbsp;</p>"
        content += "<p><strong>使用方式：</strong></p>"
        content += "<p>1.本礼品卡在绑定盒马APP后使用，全国门店/APP下单均可使用(不适用于盒小马);</p>"
        content += "<p>2.本礼品卡需下载盒马APP在[我的账户]-去绑卡中输入卡号及密码绑定后方可使用，在盒马购物结算时，将优先使用本卡支付，线下门店支持自助机使用;</p>"
        content += "<p>3.本礼品卡一经售出，概不退换;</p>"
        content += "<p>4.消费者出现退换货时，请凭消费小票等到指定服务台进行处理，具体请咨询服务台;</p>"
        content += "<p>5.本礼品卡不记名、不挂失、不可兑换现金，绑定后可多次使用，可叠加使用;</p>"
        content += "<p>6.兑换后有效期3年，请在有效期内使用;</p>"
        content += "<p>7.使用盒马礼品卡消费，盒马鲜生不再开具发票;</p>"
        content += "<p>8.请保管好自己的礼品卡号和密码。</p>"
        content += "</body></html>"
        
        # 构建收件人列表（去重处理）
        recipients_set = set()
        recipients_set.add(to_email.strip())
        
        if fixed_recipients:
            for email in fixed_recipients.split(","):
                email = email.strip()
                if email:
                    recipients_set.add(email)
        
        # 转换为列表
        recipients = list(recipients_set)
        
        try:
            # 使用全局配置的SMTP参数
            msg = MIMEText(content, "html", "utf-8")
            msg["Subject"] = Header("超越生命力的美线上讲座中奖发放", "utf-8")
            msg["From"] = SMTP_FROM
            msg["To"] = ";".join(recipients)
            
            # 根据配置选择发送方式
            if SMTP_SSL_ENABLE:
                # SMTP_SSL 已经是加密连接，不需要再调用 starttls()
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(SMTP_FROM, recipients, msg.as_string())
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                    if SMTP_STARTTLS_ENABLE:
                        server.starttls()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.sendmail(SMTP_FROM, recipients, msg.as_string())
            
            return True, "发送成功"
        
        except Exception as e:
            print(e)
            return False, f"发送失败: {str(e)}"
    
    def save_send_record(self, card_list, email):
        """保存发送记录"""
        try:
            file_exists = os.path.exists(SEND_LOG_FILE)
            
            with open(SEND_LOG_FILE, "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                
                # 写入表头（如果文件不存在）
                if not file_exists:
                    writer.writerow(["发送时间", "收件邮箱", "商品名称", "卡号", "卡密"])
                
                # 写入记录
                for card in card_list:
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        email,
                        card["商品名称"],
                        card["卡号"],
                        card["卡密"]
                    ])
            
            return True
        except Exception as e:
            self.log(f"保存发送记录失败: {str(e)}", "ERROR")
            return False
    
    def start_send(self):
        """开始发送邮件"""
        # 校验固定接收人
        recipient_errors = self.validate_fixed_recipients()
        if recipient_errors:
            error_msg = "\n".join(recipient_errors)
            self.log(f"固定接收人校验失败:\n{error_msg}", "ERROR")
            messagebox.showerror("错误", error_msg)
            return
        
        # 加载Excel数据
        df = self.load_excel()
        if df is None:
            return
        
        # 检查重复发送
        duplicates = self.check_duplicate(df)
        if duplicates:
            error_msg = "\n".join(duplicates)
            self.log(f"发现重复发送记录:\n{error_msg}", "ERROR")
            messagebox.showerror("重复发送拦截", error_msg)
            return
        
        # 按邮箱合并数据
        email_groups = self.merge_by_email(df)
        
        # 开始发送
        success_count = 0
        fail_count = 0
        
        self.log("开始发送邮件...")
        
        for idx, (email, card_list) in enumerate(email_groups.items(), 1):
            self.log(f"正在发送邮件 ({idx}/{len(email_groups)}): {email}")
            
            # 发送邮件
            success, msg = self.send_email(email, card_list, self.fixed_recipients.get())
            
            if success:
                self.log(f"✓ 成功发送到 {email}")
                success_count += 1
                
                # 保存发送记录
                self.save_send_record(card_list, email)
            else:
                self.log(f"✗ 发送失败 {email}: {msg}", "ERROR")
                fail_count += 1
            
            # 发送间隔，避免发送过快（最后一封不延迟）
            if idx < len(email_groups):
                self.log(f"等待 {SEND_INTERVAL} 秒后发送下一封...")
                time.sleep(SEND_INTERVAL)
        
        # 统计结果
        self.log(f"\n发送完成！成功: {success_count} 封, 失败: {fail_count} 封")
        messagebox.showinfo("发送完成", f"成功发送 {success_count} 封邮件，失败 {fail_count} 封")
    
    def clear_all(self):
        """清空所有内容"""
        self.file_path.set("")
        self.fixed_recipients.set("")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.excel_data = None
        self.log("已清空所有内容")

if __name__ == "__main__":
    """
    卡密批量邮件发送工具 - 主程序入口
    
    功能说明：
    1. 批量读取Excel文件中的卡密数据（商品名称、卡号、卡密、收件邮箱）
    2. 按收件邮箱合并多条卡密记录，统一发送
    3. 支持配置固定抄送/收件人
    4. 自动校验数据完整性（表头、空值、邮箱格式）
    5. 重复发送拦截：已发送的卡号/卡密组合会被记录，禁止二次发送
    6. 发送记录自动保存到 D:\\卡密发送记录\\send_log.csv
    
    使用流程：
    1. 点击"选择Excel文件"按钮，选择包含卡密数据的Excel文件
    2. （可选）在"固定抄送/收件人"输入框中输入需要抄送的邮箱，多个邮箱用英文逗号分隔
    3. 点击"开始发送"按钮，程序会自动：
       - 校验Excel文件格式和数据完整性
       - 检查是否有重复发送的卡密
       - 按邮箱合并卡密数据
       - 逐封发送邮件
       - 记录发送日志和发送记录
    4. 查看日志区域的实时反馈信息
    5. （可选）点击"清空内容"按钮清空所有输入和日志
    
    Excel文件格式要求：
    - 文件格式：.xlsx 或 .xls
    - 必需表头：商品名称、卡号、卡密、收件邮箱
    - 所有字段不能为空
    - 邮箱格式必须正确
    
    依赖库：
    - pandas：用于读取Excel文件
    - openpyxl：用于处理.xlsx格式文件
    - xlrd：用于处理.xls格式文件
    - tkinter：用于创建图形界面
    - smtplib：用于发送邮件
    """
    
    # 检查依赖（使用 print 而不是 messagebox，因为还没有创建主窗口）
    try:
        import openpyxl
        import xlrd
    except ImportError as e:
        print("依赖错误: 请先安装依赖库:")
        print("pip install pandas openpyxl xlrd")
        print(f"详细错误: {str(e)}")
        exit(1)
    
    # 创建主窗口并启动应用
    root = tk.Tk()
    app = CardEmailSender(root)
    root.mainloop()
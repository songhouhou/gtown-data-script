
# -*- coding:utf-8 -*-
import smtplib
import email
# import json
# import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.mime.image import MIMEImage
# from email.mime.base import MIMEBase
# from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr

# import urllib.request
# import ssl

# username，用户名
username = 'BosExchange@g-town.com.cn'
# password，如果开启了三方客户端安全密码需要使用网页端生成的安全密码，如果没有开启使用邮箱登录密码
password = 'Public321'
# 显示的To收信地址
rcptto = ['address1@example.net', 'address2@example.net']
# 显示的Cc收信地址
rcptcc = ['address3@example.net', 'address4@example.net']
# Bcc收信地址，密送人不会显示在邮件上，但可以收到邮件
rcptbcc = ['address5@example.net', 'address6@example.net']
receivers = rcptto + rcptcc + rcptbcc

# 构建alternative结构
msg = MIMEMultipart('alternative')
msg['Subject'] = Header('自定义信件主题')
msg['From'] = formataddr(["自定义发信昵称", username])  # 昵称+发信地址(或代发)
# list转为字符串
msg['To'] = ",".join(rcptto)
msg['Message-id'] = email.utils.make_msgid()  # message-id 用于唯一地标识每一封邮件，其格式需要遵循RFC 5322标准，通常如 <uniquestring@example.com>，其中uniquestring是邮件服务器生成的唯一标识，可能包含时间戳、随机数等信息。
msg['Date'] = email.utils.formatdate()


# 构建alternative的text/plain部分
# textplain = MIMEText('自定义TEXT纯文本部分', _subtype='plain', _charset='UTF-8')
# msg.attach(textplain)

# 构建alternative的text/html部分
texthtml = MIMEText('自定义HTML超文本部分', _subtype='html', _charset='UTF-8')
msg.attach(texthtml)

# # 发送本地附件
# files = [r'C:\Users\Downloads\test1.jpg', r'C:\Users\Downloads\test2.py.jpg']
# for t in files:
#     filename = t.rsplit('/', 1)[1]
#     part_attach1 = MIMEApplication(open(t, 'rb').read())  # 打开附件
#     part_attach1.add_header('Content-Disposition', 'attachment', filename=filename)  # 为附件命名
#     msg.attach(part_attach1)  # 添加附件

# #发送url附件
# files = [r'https://example.oss-cn-shanghai.aliyuncs.com/xxxxxxxxxxx.png']
# for t in files:
#     filename=t.rsplit('/', 1)[1]
#     response = urllib.request.urlopen(t)
#     part_attach1 = MIMEApplication(response.read())  # 打开附件，非本地文件
#     part_attach1.add_header('Content-Disposition', 'attachment', filename=filename)  # 为附件命名
#     msg.attach(part_attach1)  # 添加附件


# 发送邮件
try:
    # 若需要加密使用SSL，可以这样创建client
    # client = smtplib.SMTP_SSL('smtp.qiye.aliyun.com', 465)

    # python 3.10/3.11新版本若出现ssl握手失败,请使用下列方式处理：
    # ctxt = ssl.create_default_context()
    # ctxt.set_ciphers('DEFAULT')
    # client = smtplib.SMTP_SSL('smtp.qiye.aliyun.com', 465, context=ctxt)

    # SMTP普通端口为25
    client = smtplib.SMTP('smtp.qiye.aliyun.com', 25, timeout=10)
    # 开启DEBUG模式
    # client.set_debuglevel(0)
    # 发件人和认证地址必须一致
    client.login(username, password)
    # 备注：若想取到DATA命令返回值,可参考smtplib的sendmail封装方法:
    # 使用SMTP.mail/SMTP.rcpt/SMTP.data方法
    # print(receivers)
    client.sendmail(username, receivers, msg.as_string())  # 支持多个收件人，具体数量参考规格清单
    client.quit()
    print('邮件发送成功！')
except smtplib.SMTPConnectError as e:
    print('邮件发送失败，连接失败:', e.smtp_code, e.smtp_error)
except smtplib.SMTPAuthenticationError as e:
    print('邮件发送失败，认证错误:', e.smtp_code, e.smtp_error)
except smtplib.SMTPSenderRefused as e:
    print('邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPRecipientsRefused as e:
    print('邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPDataError as e:
    print('邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error)
except smtplib.SMTPException as e:
    print('邮件发送失败, ', str(e))
except Exception as e:
    print('邮件发送异常, ', str(e))
# 邮件通知相关

import smtplib
from email.mime.text import MIMEText

from certif_page.config.setting import EmailConfig


def send_mail(user_list=None, content="服务器出现异常"):
    password = EmailConfig.password
    email_host = EmailConfig.email_host
    send_from_user = EmailConfig.send_user  # 发件人
    if user_list is None:
        user_list = ['345592674@qq.com']

    user = "Sandie" + "<" + send_from_user + ">"

    message = MIMEText(content, _subtype='plain', _charset='utf-8')
    message['Subject'] = "认证服务器通知邮件"
    message['From'] = user
    message['To'] = ";".join(user_list)

    server = smtplib.SMTP_SSL(email_host, 465)

    server.login(send_from_user, password)
    server.sendmail(user, user_list, message.as_string())
    server.close()

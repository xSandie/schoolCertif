# 邮件通知相关

import smtplib
from email.mime.text import MIMEText


def send_mail(user_list=None, content="服务器出现异常"):
    password = 'dkpalbuarbejcbda'
    email_host = "smtp.qq.com"
    send_user = "345592674@qq.com"  # 发件人
    if user_list is None:
        user_list = ['345592674@qq.com']

    user = "Sandie" + "<" + send_user + ">"

    message = MIMEText(content, _subtype='plain', _charset='utf-8')
    message['Subject'] = "认证服务器通知邮件"
    message['From'] = user
    message['To'] = ";".join(user_list)

    server = smtplib.SMTP_SSL(email_host, 465)

    server.login(send_user, password)
    server.sendmail(user, user_list, message.as_string())
    server.close()

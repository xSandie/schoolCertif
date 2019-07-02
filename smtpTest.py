# import smtplib
# from email.mime.text import MIMEText
#
# password = ''
# email_host = "smtp.qq.com"
# send_user = ""
# user_list = ['345592674@qq.com']
#
#
#
# user = "sandie" + "<" + send_user + ">"
# content = "你好，世界"
#
# message = MIMEText(content, _subtype='plain', _charset='utf-8')
# message['Subject'] = "测试邮件"
# message['From'] = user
# message['To'] = ";".join(user_list)
#
# server = smtplib.SMTP_SSL(email_host, 465)
# # server.connect()
# server.login(send_user, password)
# server.sendmail(user, user_list, message.as_string())
# server.close()

def my_wrap(func):
    print(func.__name__.split('_')[-1])
    return func()


@my_wrap
def get():
    pass


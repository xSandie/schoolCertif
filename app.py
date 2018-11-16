import os

from flask import send_from_directory

from certif_page.create import create_app#引入自己创建的app创建方法

# UPLOAD_PATH = os.path.join(os.path.dirname(__file__),'images')
OS_PATH = os.path.dirname(__file__)

app=create_app()


if __name__=='__main__':
    app.run()#判断是否是入口文件，是的话才执行run

#下载文件接口
@app.route('/static/<school>/<filename>',methods=['GET'])
def get_image(school,filename):
    # print("get img")
    return send_from_directory(OS_PATH+'/static/'+school,filename)
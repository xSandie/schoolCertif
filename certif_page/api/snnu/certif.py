# -*- coding:utf-8 -*- 
import re
import requests
from flask import Blueprint, jsonify, request, send_from_directory
from sqlalchemy import desc

from certif_page.libs.filehelper import img_net_prefix
from certif_page.models.base import db
from certif_page.models.snnu import SnnuCookie
from app import OS_PATH


snnu=Blueprint('snnu',__name__)


@snnu.route('/certif',methods=['POST'])
def certif():
    req_arg = request.form
    db_data = SnnuCookie.query.filter_by(userId=req_arg['userId']).order_by(desc("id")).first()#降序排列取最后一个
    my_cookie = db_data.JSESSIONID
    my_cookies={
        'JSESSIONID':my_cookie
    }

    certif_url='http://219.244.71.113/loginAction.do'
    name_and_schoolNum_url='http://219.244.71.113/menu/top.jsp'
    sex_url='http://219.244.71.113/xjInfoAction.do?oper=xjxx'
    s = requests.session()
    info = {'zjh': req_arg['zjh'], 'mm': req_arg['mm'], 'v_yzm': req_arg['yzm']}

    rename_schoolNum=re.compile("当前用户:(\d*)\((\S*)\)")
    resex =re.compile('性别:&nbsp;\s*</td>\s*<td align="left" width="275">\s*(\S*)\s*</td>')

    html=s.post(certif_url, data=info,cookies=my_cookies)
    name_and_schoolNum_html=s.get(name_and_schoolNum_url,cookies=my_cookies)
    sex_html=s.get(sex_url,cookies=my_cookies)

    name_and_schoolNum=re.findall(rename_schoolNum,name_and_schoolNum_html.text)#第一个是学号，第二个是姓名
    sex=re.findall(resex,sex_html.text)

    #提取具体数据
    try:
        name_and_schoolNum=list(name_and_schoolNum[0])
        sex=sex[0]

        # print(name_and_schoolNum)
        # print(sex)

        if sex and name_and_schoolNum:
            with db.auto_commit():
                db_data.userName=name_and_schoolNum[1]  #是定义的colume名而不是数据库列名
                db_data.schoolNum=name_and_schoolNum[0]
                db_data.sex=sex
            res_dict={
                'userId': req_arg['userId'],
                'status': 1,
                'name':name_and_schoolNum[1],
                'schoolNum':name_and_schoolNum[0],
                'sex':sex
            }
            return jsonify(res_dict)
    except Exception as e:
        #认证失败逻辑需要再写一下,再次去获取验证码
        main_url = 'http://219.244.71.113/'

        s = requests.session()
        img = None
        html = s.get(main_url)
        my_cookie = html.cookies['JSESSIONID']
        cookie_dict = dict(html.cookies)

        img_local_url = "/static/snnu/" + str(req_arg['userId']) + '.jpg'
        img_name = OS_PATH + img_local_url

        if get_img(img_name, cookie_dict):
            with db.auto_commit():
                snnu_cookie = SnnuCookie()
                snnu_cookie.userId = str(req_arg['userId'])
                snnu_cookie.JSESSIONID = my_cookie
                snnu_cookie.imgUrl = img_local_url
                db.session.add(snnu_cookie)

            error_get = {
                'userId': req_arg['userId'],
                'imgUrl': img_net_prefix + img_local_url,
                'status': 0
            }

            return jsonify(error_get)


@snnu.route('/get',methods=['POST'])
def get():
    # print(request.args)
    req_arg=request.form
    main_url = 'http://219.244.71.113/'

    s = requests.session()
    img = None
    html = s.get(main_url)
    my_cookie=html.cookies['JSESSIONID']
    cookie_dict=dict(html.cookies)

    img_local_url="/static/snnu/"+str(req_arg['userId'])+'.jpg'
    img_name=OS_PATH+img_local_url

    if get_img(img_name,cookie_dict):
        with db.auto_commit():
            snnu_cookie=SnnuCookie()
            snnu_cookie.userId=str(req_arg['userId'])
            snnu_cookie.JSESSIONID=my_cookie
            snnu_cookie.imgUrl=img_local_url
            db.session.add(snnu_cookie)

        first_get={
            'userId':req_arg['userId'],
            'imgUrl':img_net_prefix + img_local_url
        }

        return jsonify(first_get)
    else:
        error={
            'userId': req_arg['userId'],
            'error':'file_save_error'
        }
        return jsonify(error)

#获取图片并存储
def get_img(img_name,my_cookies):
    img_url = 'http://219.244.71.113/validateCodeAction.do?'
    img_get = requests.get(img_url, cookies=my_cookies)
    try:
        with open(img_name, 'wb') as f:
            f.write(img_get.content)
        return True
    except Exception as e:
        return False




# @snnu.route('/getagain',methods=['POST'])
# def getagain():
#     req_arg = request.args
#     db_data = SnnuCookie.query.filter_by(userId=req_arg['userId']).order_by(desc("id")).first()
#     my_cookie=db_data.JSESSIONID
#
#     db_cookies = {'JSESSIONID': my_cookie}
#     img_local_url = "/static/snnu/" + str(req_arg['userId']) + '.jpg'
#     img_name = OS_PATH + img_local_url
#
#     if get_img(img_name,db_cookies):
#         again_get = {
#             'userId': req_arg['userId'],
#             'imgUrl': img_local_url
#         }
#         return jsonify(again_get)
#     else:
#         error = {
#             'userId': req_arg['userId'],
#             'error': 'file_save_error'
#         }
#         return jsonify(error)
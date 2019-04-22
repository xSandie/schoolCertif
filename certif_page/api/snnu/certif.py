# -*- coding:utf-8 -*- 
import json
import os
import re
import requests
from flask import Blueprint, jsonify, request, abort, current_app, logging
from lxml import etree

from certif_page.api.IDENTITY import BENKE, MASTER
from certif_page.api.snnu.URL import benke_get_url, benke_get_pic_url, benke_certif_url, benke_name_schoolNum_url, \
    benke_sex_url, master_main_url, master_code_url, master_certif_url, master_sex_name_url
from certif_page.libs.abbr2id import abbr2id
from certif_page.libs.redis_conn import cookie_redis
from certif_page.libs.token import check_token
from certif_page.models.RemoteUrl import RemoteUrl
from certif_page.models.School import School
from certif_page.models.Success import Success
from certif_page.models.base import db
from app import OS_PATH


snnu=Blueprint('snnu',__name__)

#获取图片并存储
def get_img(img_name,my_cookies,url):
    img_get = requests.get(url, cookies=my_cookies)
    try:
        with open(img_name, 'wb') as f:
            f.write(img_get.content)
        return True
    except Exception as e:
        return False

#todo 本科外网认证，获取二维码图片
def local_get_benke():
    pass

#todo 本科外网认证，通过认证
def local_certif_benke():
    pass

#todo 本科内网认证，获取二维码图片
def remote_get_benke():
    pass

#todo 本科内网认证，通过认证
def remote_certif_benke():
    pass

#todo 研究生外网认证，获取二维码图片
def local_get_master():
    pass

#todo 研究生外网认证，通过认证
def local_certif_master():
    pass

#todo 研究生内网认证，获取二维码图片
def remote_get_master():
    pass

#todo 研究生内网认证，通过认证
def remote_certif_master():
    pass

#todo 查询redis确认内网是否存活
def is_alive():
    pass


#重命名认证成功后的二维码图片
def rename_code(pic_name,user_id):
    save_loop=True
    count=0
    while(save_loop):
        try:
            old_pic_loc = OS_PATH+'/static/snnu/'+ str(user_id) + '.jpg'
            new_pic_name = OS_PATH + '/static/snnu/' + str(pic_name) + '(' + str(user_id) +str(count)+ ')' + '.jpg'
            os.rename(old_pic_loc, new_pic_name)
            #改名成功就跳出循环
            save_loop=False
        except Exception as e:
            count+=1
    return True



#本科生认证
def benke_certif(req_arg, school_id):
    # db_data = SnnuCookie.query.filter_by(userId=str(req_arg['user_id'])).order_by(desc("id")).first()  # 降序排列取最后一个
    # my_cookie = db_data.JSESSIONID
    cookie_dict = cookie_redis.get(school_id + ':' + str(req_arg['user_id']))
    if cookie_dict is None:return None
    my_cookies = json.loads(cookie_dict.decode('utf-8'))

    s = requests.session()
    info = {'zjh': req_arg['account'], 'mm': req_arg['password'], 'v_yzm': req_arg['verification_code']}

    rename_schoolNum = re.compile("当前用户:(\d*)\((\S*)\)")
    resex = re.compile('性别:&nbsp;\s*</td>\s*<td align="left" width="275">\s*(\S*)\s*</td>')
    re_specialty = re.compile("专业:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_class = re.compile("班级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_grade = re.compile("年级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")


    html = s.post(benke_certif_url, data=info, cookies=my_cookies)
    #认证完成，以下开始获取相关信息

    name_and_schoolNum_html = s.get(benke_name_schoolNum_url, cookies=my_cookies)
    sex_html = s.get(benke_sex_url, cookies=my_cookies)
    # course_html = s.get(courses_table, cookies=my_cookies)

    name_and_schoolNum = re.findall(rename_schoolNum, name_and_schoolNum_html.text)  # 第一个是学号，第二个是姓名
    sex = re.findall(resex, sex_html.text)
    major = re.findall(re_specialty, sex_html.text)[0]
    clss = re.findall(re_class, sex_html.text)[0]
    grade = re.findall(re_grade, sex_html.text)[0]

    #todo 保存用户照片
    portrait_url = benke_get_url+'xjInfoAction.do?oper=img'
    save_portrait_uri = OS_PATH+"/static/snnu/portrait/" + str(req_arg['user_id']) + '.jpg'
    get_img(save_portrait_uri,my_cookies,portrait_url)

    # 提取具体数据
    try:
        name_and_schoolNum = list(name_and_schoolNum[0])
        sex = sex[0]

        if sex and name_and_schoolNum:
            #表示都获取成功了
            with db.auto_commit():
                success = Success()
                success.schoolId = int(school_id)
                success.portraitUri = "/static/snnu/portrait/" + str(req_arg['user_id']) + '.jpg'
                success.info = 'name:'+name_and_schoolNum[1]+','+'school_numb:'+name_and_schoolNum[0]+','+\
                'sex:'+ sex+','+'identity:1,'+'major:'+major+','+'class:'+clss+','+\
                'grade:'+grade+',{{'+sex_html.text+'}}' #存储网页源码，方便以后分析
                db.session.add(success)
            result_dict = {
                'user_id': req_arg['user_id'],
                'status': 1,
                'name': name_and_schoolNum[1],
                'school_numb': name_and_schoolNum[0],
                'sex': sex,
                'identity':1,
                'major':major,
                'class':clss,
                'grade':grade
            }
            # 重命名用户认证用的二维码
            rename_code(req_arg['verification_code'], req_arg['user_id'])

        else:
            result_dict={
                'error': 'fail to get sex and name'
            }
    except Exception as e:
        print(e)
        result_dict=benke_get(req_arg,school_id)
        result_dict['status']=0
        # 认证失败逻辑需要再写一下,再次去获取验证码



    return result_dict

#本科生获取验证码
def benke_get(req_arg, school_id):
    s = requests.session()
    html = s.get(benke_get_url)
    # my_cookie = html.cookies['JSESSIONID']
    cookie_dict = dict(html.cookies)

    img_local_url = "/static/snnu/" + str(req_arg['user_id']) + '.jpg'
    img_name = OS_PATH + img_local_url

    if get_img(img_name, cookie_dict,benke_get_pic_url):
        cookie_redis.setex(school_id+':'+str(req_arg['user_id']),
                           current_app.config['COOKIE_LIVE_TIME'], json.dumps(cookie_dict))
        result_dict = {
            'user_id': req_arg['user_id'],
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        result_dict = {
            'user_id': req_arg['user_id'],
            'error': 'file_save_error'
        }

    return result_dict

#研究生相关
def master_certif(req_arg, school_id):
    cookie_dict = cookie_redis.get(school_id+':'+str(req_arg['user_id']))
    if not cookie_dict:
        return None#过期
    cookie_dict = json.loads(cookie_dict)
    my_cookie = cookie_dict.get('JSESSIONID')
    my_cookies = {
        'ASP.NET_SessionId': my_cookie
    }
    header = {
        'Host': 'yjssys.snnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://yjssys.snnu.edu.cn/gstudent/ReLogin.aspx?ReturnUrl=/Gstudent/loging.aspx',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'keep-alive'
    }

    info = {
        'ctl00$contentParent$UserName': req_arg['account'],
        'ctl00$contentParent$PassWord': req_arg['password'],
        'ctl00$contentParent$ValidateCode': req_arg['verification_code'],
    }
    info = {**info, **cookie_dict}#合并两个dict
    renzheng = requests.post(master_certif_url,
                             data=info, headers=header, cookies=my_cookies)
    name_html = requests.get(master_sex_name_url, cookies=my_cookies)
    try:
        sex_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[2]/td[2]//text()'
        name_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[1]/td[4]//text()'

        tree = etree.HTML(name_html.text)
        sex = tree.xpath(sex_xpath)
        name = tree.xpath(name_xpath)
        name_fin = str(name[0]).strip()
        sex_fin = str(sex[0]).strip()

        result_dict = {
            'user_id': req_arg['user_id'],
            'status': 1,
            'name': name_fin,
            'school_numb': req_arg['account'],
            'sex': sex_fin,
            'identity': 2
        }
        with db.auto_commit():
            success = Success()
            success.schoolId = int(school_id)
            success.userId = int(req_arg['user_id'])
            success.info = 'user_id:'+req_arg['user_id']+","+\
            'name:'+name_fin+','+'school_numb:' + \
            req_arg['account']+','+'sex:'+sex_fin+','+'identity:2'
        # 重命名用户认证用的二维码
        rename_code(req_arg['verification_code'], req_arg['user_id'])

    except Exception as e:
        #获取姓名出错逻辑
        result_dict = master_get(req_arg,school_id)
        result_dict['status'] = 0

    return result_dict


def master_get(req_arg, school_id):
    s = requests.session()
    html = s.get(master_main_url)
    my_cookie = html.cookies.get('ASP.NET_SessionId')
    cookie_dict = dict(html.cookies)

    img_local_url = "/static/snnu/" + str(req_arg['user_id']) + '.jpg'
    img_name = OS_PATH + img_local_url

    if get_img(img_name, cookie_dict,master_code_url):
        # 获取csrf_token
        CSRF_XPATH_1 = '//*[@id="__EVENTVALIDATION"]/@value'
        CSRF_XPATH_2 = '//*[@id="__VIEWSTATEGENERATOR"]/@value'
        CSRF_XPATH_3 = '//*[@id="__VIEWSTATE"]/@value'

        orgin_tree = etree.HTML(html.content)
        __EVENTVALIDATION = orgin_tree.xpath(CSRF_XPATH_1)
        __VIEWSTATEGENERATOR = orgin_tree.xpath(CSRF_XPATH_2)
        __VIEWSTATE = orgin_tree.xpath(CSRF_XPATH_3)

        csrf__EVENTVALIDATION = str(__EVENTVALIDATION[0])
        csrf__VIEWSTATEGENERATOR = str(__VIEWSTATEGENERATOR[0])
        csrf__VIEWSTATE = str(__VIEWSTATE[0])

        #cookie school_id+':'+str(req_arg['user_id'])
        cookie_dict = {
            '__EVENTVALIDATION': csrf__EVENTVALIDATION,
            '__VIEWSTATEGENERATOR': csrf__VIEWSTATEGENERATOR,
            '__VIEWSTATE': csrf__VIEWSTATE,
            '__EVENTTARGET': 'ctl00$contentParent$btLogin',
            '__EVENTARGUMENT': '',
            'JSESSIONID': my_cookie
        }
        cookie_redis.setex(school_id+':'+str(req_arg['user_id']),current_app.config['COOKIE_LIVE_TIME'],
                         json.dumps(cookie_dict))
        result_dict = {
            'user_id': req_arg['user_id'],
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        result_dict = {
            'user_id': req_arg['user_id'],
            'error': 'file_save_error'
        }
    return result_dict




#todo 教师相关
def teacher_certif():
    pass

def teacher_get():
    pass



@snnu.route('/certif',methods=['POST'])
def certif():
    school_id = str(abbr2id('snnu'))
    req_args = request.form
    req_args = req_args.to_dict()
    if check_token(req_args.get('token')):
        req_args['user_id'] = str(req_args['user_id'])#防止传int
        if int(req_args.get('identity',1)) == BENKE:
            certif_res = benke_certif(req_args, school_id)
        elif int(req_args.get('identity'))==MASTER:
            certif_res = master_certif(req_args, school_id)
        else:
            abort(400)
    return jsonify(certif_res)


@snnu.route('/get',methods=['POST'])
def get():
    _ = School()
    _ = RemoteUrl()
    school_id = str(abbr2id('snnu'))
    req_args = request.form
    req_args = req_args.to_dict()

    if check_token(req_args.get('token')):
        req_args['user_id'] = str(req_args['user_id'])  # 防止传int

        if int(req_args.get('identity',1)) == BENKE:
            result_dict=benke_get(req_args, school_id)
        elif int(req_args.get('identity'))==MASTER:
            result_dict=master_get(req_args, school_id)
    else:
        abort(400)
    return jsonify(result_dict)






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
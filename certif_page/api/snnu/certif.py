# -*- coding:utf-8 -*- 
import json
import re
from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, request, abort, current_app
from lxml import etree

from certif_page.api.IDENTITY import BENKE, MASTER
from certif_page.api.snnu.URL import benke_get_url, benke_get_pic_url, benke_certif_url, benke_name_schoolNum_url, \
    benke_sex_url, master_main_url, master_code_url, master_certif_url, master_sex_name_url
from certif_page.libs.abbr2id import abbr2id
from certif_page.libs.local_remote import check_alive, try_local, check_remoteOrLocal
from certif_page.libs.debug import debug
from certif_page.libs.image import rename_code, get_img, swap_remote_url
from certif_page.libs.redis_conn import cookie_redis, alive_redis
from certif_page.libs.token import check_token
from certif_page.models.RemoteUrl import RemoteUrl
from certif_page.models.School import School
from certif_page.models.Success import Success
from certif_page.models.base import db
from app import OS_PATH


snnu = Blueprint('snnu', __name__)
school_abbr = 'snnu'
DEBUG = False  # 是否开启调试
DEBUG_URL = 'http://127.0.0.1:10000'  # 调试时的转发地址


# todo 本科内网认证，获取二维码图片
def remote_get_benke(req_args, school_id):
    school_id = int(school_id)
    url_dic = alive_redis.get(str(school_id))  # 得到dict
    url = url_dic + 'snnu/get'
    pass

# todo 本科内网认证，通过认证


def remote_certif_benke():
    pass

# todo 研究生内网认证，获取二维码图片


def remote_get_master():
    pass

# todo 研究生内网认证，通过认证


def remote_certif_master(req_args, school_id):
    school_id = int(school_id)
    url_dic = alive_redis.get(str(school_id))  # 得到dict
    url = url_dic + 'snnu/certif'


# 外网本科生认证
def benke_certif(req_arg: dict, school_id: str) -> dict:
    result_dict = {}
    # db_data = SnnuCookie.query.filter_by(userId=str(req_arg['user_id'])).order_by(desc("id")).first()  # 降序排列取最后一个
    # my_cookie = db_data.JSESSIONID
    cookie_dict = cookie_redis.get(school_id + ':' + str(req_arg['user_id']))

    if not cookie_dict:
        result_dict['status'] = 0
        return result_dict  # 过期

    my_cookies = json.loads(cookie_dict.decode('utf-8'))

    s = requests.session()
    info = {
        'zjh': req_arg['account'],
        'mm': req_arg['password'],
        'v_yzm': req_arg['verification_code']}

    rename_schoolNum = re.compile(r"当前用户:(\d*)\((\S*)\)")
    resex = re.compile(
        r'性别:&nbsp;\s*</td>\s*<td align="left" width="275">\s*(\S*)\s*</td>')
    re_specialty = re.compile(r"专业:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_class = re.compile(r"班级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_grade = re.compile(r"年级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")

    _ = s.post(benke_certif_url, data=info, cookies=my_cookies)
    # 认证完成，以下开始获取相关信息

    name_and_schoolNum_html = s.get(
        benke_name_schoolNum_url,
        cookies=my_cookies)
    sex_html = s.get(benke_sex_url, cookies=my_cookies)
    # course_html = s.get(courses_table, cookies=my_cookies)

    name_and_schoolNum = re.findall(
        rename_schoolNum,
        name_and_schoolNum_html.text)  # 第一个是学号，第二个是姓名
    sex = re.findall(resex, sex_html.text)
    major = re.findall(re_specialty, sex_html.text)[0]
    clss = re.findall(re_class, sex_html.text)[0]
    grade = re.findall(re_grade, sex_html.text)[0]

    # todo 保存用户照片
    portrait_url = benke_get_url + 'xjInfoAction.do?oper=img'
    save_portrait_uri = OS_PATH + "/static/snnu/portrait/" + \
        str(req_arg['user_id']) + '.jpg'
    get_img(
        img_name=save_portrait_uri,
        my_cookies=my_cookies,
        url=portrait_url)

    # 提取具体数据
    try:
        name_and_schoolNum = list(name_and_schoolNum[0])
        sex = sex[0]

        if sex and name_and_schoolNum:
            # 表示都获取成功了
            with db.auto_commit():
                success = Success()
                success.schoolId = int(school_id)
                success.portraitUri = "/static/snnu/portrait/" + \
                    str(req_arg['user_id']) + '.jpg'
                success.info = 'name:' + name_and_schoolNum[1] + ',' + 'school_numb:' + name_and_schoolNum[0] + ',' +\
                    'sex:' + sex + ',' + 'identity:1,' + 'major:' + major + ',' + 'class:' + clss + ',' +\
                    'grade:' + grade + ',{{' + sex_html.text + '}}'  # 存储网页源码，方便以后分析
                db.session.add(success)
            result_dict = {
                'user_id': req_arg['user_id'],
                'status': 1,
                'name': name_and_schoolNum[1],
                'school_numb': name_and_schoolNum[0],
                'sex': sex,
                'identity': 1,
                'major': major,
                'class': clss,
                'grade': grade
            }
            # 重命名用户认证用的二维码
            rename_code(
                pic_name=req_arg['verification_code'],
                user_id=req_arg['user_id'],
                school_abbr=school_abbr)

        else:
            result_dict = {
                'error': 'fail to get sex and name'
            }
    except Exception as _:
        raise IndexError
        # print(e)
        # result_dict=benke_get(req_arg,school_id)
        # result_dict['status'] = 0
        # 认证失败逻辑需要再写一下,再次去获取验证码
    return result_dict

# 外网本科生验证码


def benke_get(req_arg: dict, school_id: str) -> dict:
    s = requests.session()
    html = s.get(benke_get_url)
    # my_cookie = html.cookies['JSESSIONID']
    cookie_dict = dict(html.cookies)
    img_local_url = "/static/snnu/" + str(req_arg['user_id']) + '.jpg'
    img_name = OS_PATH + img_local_url
    if get_img(
            img_name=img_name,
            my_cookies=cookie_dict,
            url=benke_get_pic_url):
        cookie_redis.setex(
            school_id + ':' + str(
                req_arg['user_id']),
            current_app.config['COOKIE_LIVE_TIME'],
            json.dumps(cookie_dict))
        result_dict = {
            'user_id': req_arg['user_id'],
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        raise OverflowError
    return result_dict

# 外网研究生认证


def master_certif(req_arg: dict, school_id: str) -> dict:
    result_dict = {}
    cookie_dict = cookie_redis.get(school_id + ':' + str(req_arg['user_id']))

    if not cookie_dict:
        result_dict['status'] = 0
        return result_dict  # 过期

    cookie_dict = json.loads(cookie_dict)
    my_cookie = cookie_dict.get('JSESSIONID')
    my_cookies = {
        'ASP.NET_SessionId': my_cookie,
        'LoginType': 'LoginType=1'
    }
    header = {
        'Host': 'yjssys.snnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://yjssys.snnu.edu.cn/',
        'X-Requested-With': 'XMLHttpRequest',
        'X-MicrosoftAjax': 'Delta=true',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
    }

    info = {
        'UserName': str(req_arg['account']),
        'PassWord': str(req_arg['password']),
        'ValidateCode': str(req_arg['verification_code']),
        'drpLoginType': 1,
        '__ASYNCPOST': 'true',
    }
    new_info = urlencode({**cookie_dict, **info})  # 合并两个dict#合并两个dict
    _ = requests.post(master_certif_url,
                      data=new_info, headers=header, cookies=my_cookies)
    name_html = requests.get(master_sex_name_url, cookies=my_cookies)

    try:
        # sex_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[2]/td[2]//text()'
        # name_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[1]/td[4]//text()'
        #
        # tree = etree.HTML(name_html.text)
        # sex = tree.xpath(sex_xpath)
        # name = tree.xpath(name_xpath)
        # name_fin = str(name[0]).strip()
        # sex_fin = str(sex[0]).strip()
        re_name = re.compile(r'姓名\s*</td>\s*<td.*?>\s*(\S*)\s*</td>')
        re_sex = re.compile(r'性别\s*</td>\s*<td.*?>\s*(\S*)\s*</td>')
        # re_schoolNumb = re.compile("学号\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")

        name_fin = re.findall(re_name, name_html.text)[0].strip()
        sex_fin = re.findall(re_sex, name_html.text)[0].strip()

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
            success.info = 'user_id:' + req_arg['user_id'] + "," +\
                'name:' + name_fin + ',' + 'school_numb:' + \
                req_arg['account'] + ',' + 'sex:' + sex_fin + ',' + 'identity:2'
        # 重命名用户认证用的二维码
        rename_code(
            pic_name=req_arg['verification_code'],
            user_id=req_arg['user_id'],
            school_abbr=school_abbr)

    except Exception as e:
        raise IndexError
        # 获取姓名出错逻辑
        # result_dict = master_get(req_arg,school_id)
        # result_dict['status'] = 0
    return result_dict

# 外网研究生验证码


def master_get(req_arg: dict, school_id: str) -> dict:
    s = requests.session()
    header = {
        'Host': 'yjssys.snnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1'}
    html = s.get(master_code_url, headers=header)
    my_cookie = html.cookies.get('ASP.NET_SessionId')
    cookie_dict = dict(html.cookies)

    img_local_url = "/static/snnu/" + str(req_arg['user_id']) + '.jpg'
    img_name = OS_PATH + img_local_url

    if get_img(img_name=img_name, my_cookies=cookie_dict, url=master_code_url):
        # 获取csrf_token
        html = s.get(master_main_url, headers=header, cookies=cookie_dict)

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

        # cookie school_id+':'+str(req_arg['user_id'])
        cookie_dict = {
            'ScriptManager1': 'UpdatePanel2|btLogin',
            '__EVENTTARGET': 'btLogin',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': csrf__VIEWSTATE,
            '__VIEWSTATEGENERATOR': csrf__VIEWSTATEGENERATOR,
            '__EVENTVALIDATION': csrf__EVENTVALIDATION,
            'JSESSIONID': my_cookie,
        }
        cookie_redis.setex(
            school_id + ':' + str(
                req_arg['user_id']),
            current_app.config['COOKIE_LIVE_TIME'],
            json.dumps(cookie_dict))
        result_dict = {
            'user_id': req_arg['user_id'],
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        raise OverflowError
    return result_dict


@snnu.route('/certif', methods=['POST'])
def certif():
    school_id = str(abbr2id('snnu'))
    req_args = request.form
    req_args = req_args.to_dict()
    req_args['user_id'] = str(req_args['user_id'])  # 防止传int
    certif_res = {}
    if DEBUG:
        certif_res = {**debug(req_args, DEBUG_URL, school_abbr)}
    else:
        if check_token(req_args.get('token')):
            if check_alive(school_id, alive_redis):
                # todo 发起内网请求，失败后报错，通知管理员
                pass
            else:
                if int(req_args.get('identity', 1)) == BENKE:
                    certif_res = benke_certif(req_args, school_id)
                elif int(req_args.get('identity')) == MASTER:
                    certif_res = master_certif(req_args, school_id)
                else:
                    abort(400)
    return jsonify(certif_res)


@snnu.route('/get', methods=['POST'])
def get():
    _ = School()
    _ = RemoteUrl()
    school_id = str(abbr2id(school_abbr))
    req_args = request.form
    req_args = req_args.to_dict()
    req_args['user_id'] = str(req_args['user_id'])  # 防止传int
    res_dict = {}
    if DEBUG:
        res_dict = {**debug(req_args, DEBUG_URL, school_abbr)}
    else:
        if check_token(req_args.get('token')):
            if check_remoteOrLocal(school_abbr, alive_redis):
                # todo 尝试内网请求
                if check_alive(school_id, alive_redis):
                    # todo 发起内网请求，失败后报错，通知管理员
                    pass
                else:  # todo 内网也挂了，通知管理员，可以返回占位img
                    pass
            else:
                # todo 外网请求
                with try_local(req_args=req_args, school_id=school_id, get_func=place_holder,
                               local_func=local_get, res_dict=res_dict):
                    pass
        else:
            abort(400)
    return jsonify(res_dict)

# todo 发起外网请求


def local_get(req_args: dict, school_id: str) -> dict:
    identity = int(req_args.get('identity', 1))  # 默认本科
    if identity == BENKE:
        return benke_get(req_args, school_id)
    elif identity == MASTER:
        return master_get(req_args, school_id)
    else:
        return {'status': 4}


def local_certif(req_args: dict, school_id: str):
    identity = int(req_args.get('identity', 1))  # 默认本科
    if identity == BENKE:
        return benke_certif(req_args, school_id)
    elif identity == MASTER:
        return master_certif(req_args, school_id)
    else:
        return {'status': 4}


# todo 内网请求
def remote_get():
    pass


def remote_certif():
    pass

# get时的占位func,可以返回占位验证码


def place_holder(req_args, school_id):
    return {'status': 4}


def rescue_input_error(*, certif_res, req_args, school_id: str):
    # todo 预计是账号密码错误，进行补救
    if certif_res.get('status') == 0:
        if check_remoteOrLocal(int(school_id)):
            # 通过内网，内网会自动补救返回img_url
            certif_res['img_url'] = swap_remote_url(
                img_url=certif_res.get('img_url'),
                user_id=req_args.get('user_id'),
                school_abbr=school_abbr)
        else:  # 通过外网
            if int(req_args.get('identity', 1)) == BENKE:
                certif_res = benke_get(req_args, school_id)
            elif int(req_args.get('identity')) == MASTER:
                certif_res = master_get(req_args, school_id)

        certif_res['status'] = 0

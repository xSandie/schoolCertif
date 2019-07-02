# -*- coding:utf-8 -*- 
import json
import re
from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, request, current_app
from lxml import etree

from certif_page.api.IDENTITY import BENKE, MASTER
from certif_page.api.snnu.URL import benke_get_url, benke_get_pic_url, benke_certif_url, benke_name_schoolNum_url, \
    benke_sex_url, master_main_url, master_code_url, master_certif_url, master_sex_name_url
from certif_page.api.snnu.schema import CertifSchema, GetSchema, ChangeSchema
from certif_page.libs.abbr2id import abbr2id
from certif_page.libs.image import rename_code, get_img
from certif_page.libs.local_remote import check_remoteOrLocal
from certif_page.libs.redis_conn import cookie_redis
from certif_page.libs.args_and_docs.use_small_args import use_small_args
from certif_page.models.RemoteProxy import RemoteProxy
from certif_page.models.Success import Success
from certif_page.models.base import db

snnu = Blueprint('snnu', __name__)
school_abbr = 'snnu'

@snnu.route('/change_route',methods=['POST'])
@use_small_args(ChangeSchema)
def change_route(account, password):
    """改变内外网状态
    :::ChangeSchema:::
    :return:
    """
    return jsonify({})



@snnu.route('/certif', methods=['POST'])
@use_small_args(CertifSchema)
def certif_post(args):
    """认证请求
    :::CertifSchema:::
    """
    school_id = str(abbr2id('snnu'))
    req_args = {}
    req_args['user_id'] = str(args['user_id'])  # 防止传int
    certif_res = {}

    if check_remoteOrLocal(school_id):
        # todo 尝试内网请求
        pass
    else:
        # todo 外网请求
        pass

    return jsonify(certif_res)


@snnu.route('/get', methods=['POST'])
@use_small_args(GetSchema)
def certif_get(user_id, identity):
    """获取验证码和cookie
    :::GetSchema:::
    """
    school_id = str(abbr2id(school_abbr))
    res_dict = {}
    if check_remoteOrLocal(school_id):
        # todo 内网请求
        if identity == MASTER:
            master_get(user_id, school_id, True)
        else:
            benke_get(user_id, school_id, True)
    else:
        # todo 外网请求

        pass

    return jsonify(res_dict)


# 外网本科生认证
def benke_certif(req_arg: dict, school_id: str, remote_or_local: bool) -> dict:
    result_dict = {}
    # 加载remote_proxy
    if remote_or_local:
        remote_proxy_obj = RemoteProxy.query.filter_by(schoolId=int(school_id)).first()
        remote_proxy = {
            "http": remote_proxy_obj.remoteProxy,
            "https": remote_proxy_obj.remoteProxy
        }
    else:
        remote_proxy = None

    info = {
        'zjh': req_arg['account'],
        'mm': req_arg['password'],
        'v_yzm': req_arg['verification_code']
    }
    cookie_dict = cookie_redis.get(school_id + ':' + str(req_arg['user_id']))

    if not cookie_dict:
        result_dict['status'] = 0
        return result_dict  # 过期

    my_cookies = json.loads(cookie_dict.decode('utf-8'))

    re_name_and_school_numb = re.compile(r"当前用户:(\d*)\((\S*)\)")
    re_sex = re.compile(
        r'性别:&nbsp;\s*</td>\s*<td align="left" width="275">\s*(\S*)\s*</td>')
    re_specialty = re.compile(r"专业:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_class = re.compile(r"班级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
    re_grade = re.compile(r"年级:&nbsp;\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")

    s = requests.session()
    # 集中请求
    _ = s.post(benke_certif_url, proxies=remote_proxy, data=info, cookies=my_cookies)
    # 认证完成，以下开始获取相关信息

    name_and_schoolNum_html = s.get(
        benke_name_schoolNum_url,
        proxies=remote_proxy,
        cookies=my_cookies)
    sex_html = s.get(benke_sex_url, proxies=remote_proxy, cookies=my_cookies)
    # course_html = s.get(courses_table, cookies=my_cookies)

    name_and_schoolNum = re.findall(
        re_name_and_school_numb,
        name_and_schoolNum_html.text)  # 第一个是学号，第二个是姓名
    sex = re.findall(re_sex, sex_html.text)
    major = re.findall(re_specialty, sex_html.text)[0]
    clss = re.findall(re_class, sex_html.text)[0]
    grade = re.findall(re_grade, sex_html.text)[0]

    # todo 保存用户照片
    from app import OS_PATH
    portrait_url = benke_get_url + 'xjInfoAction.do?oper=img'
    save_portrait_uri = OS_PATH + "/static/snnu/portrait/" + \
                        str(req_arg['user_id']) + '.jpg'
    get_img(
        proxies=remote_proxy,
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
                success.userId = int(req_arg['user_id'])
                success.portraitUri = "/static/snnu/portrait/" + \
                                      str(req_arg['user_id']) + '.jpg'
                success.info = 'name:' + name_and_schoolNum[1] + ',' + 'school_numb:' + name_and_schoolNum[0] + ',' + \
                               'sex:' + sex + ',' + 'identity:1,' + 'major:' + major + ',' + 'class:' + clss + ',' + \
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
        result_dict = benke_get(req_arg['user_id'], school_id, remote_or_local)
        result_dict['status'] = 0
        # 认证失败逻辑需要再写一下,再次去获取验证码
    return result_dict


# 本科生验证码
def benke_get(user_id: dict, school_id: str, remote_or_local: bool) -> dict:
    """
    本科生获取验证码 和 cookie
    :param user_id: 参数字典
    :param school_id: 学校id
    :param remote_or_local: 判断是否使用代理进行remote内网认证，True使用代理，False不使用代理
    :return:
    """
    remote_proxy = None
    if remote_or_local:
        remote_proxy_obj = RemoteProxy.query.filter_by(schoolId=school_id).first()
        remote_proxy = {
            "http": remote_proxy_obj.remoteProxy,
            "https": remote_proxy_obj.remoteProxy
        }
    from app import OS_PATH
    s = requests.session()
    html = s.get(benke_get_url, proxies=remote_proxy)
    # my_cookie = html.cookies['JSESSIONID']
    cookie_dict = dict(html.cookies)
    img_local_url = "/static/snnu/" + str(user_id) + '.jpg'
    img_name = OS_PATH + img_local_url
    if get_img(
            proxies=remote_proxy,
            img_name=img_name,
            my_cookies=cookie_dict,
            url=benke_get_pic_url):
        cookie_redis.setex(
            school_id + ':' + str(
                user_id),
            current_app.config['COOKIE_LIVE_TIME'],
            json.dumps(cookie_dict))
        result_dict = {
            'user_id': user_id,
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        raise OverflowError
    return result_dict


# 研究生认证
def master_certif(req_arg: dict, school_id: str, remote_or_local: bool) -> dict:
    result_dict = {}
    cookie_dict = cookie_redis.get(school_id + ':' + str(req_arg['user_id']))
    if not cookie_dict:
        result_dict['status'] = 0
        return result_dict  # 过期

    remote_proxy = None
    if remote_or_local:
        remote_proxy_obj = RemoteProxy.query.filter_by(schoolId=school_id).first()
        remote_proxy = {
            "http": remote_proxy_obj.remoteProxy,
            "https": remote_proxy_obj.remoteProxy
        }

    info = {
        'UserName': str(req_arg['account']),
        'PassWord': str(req_arg['password']),
        'ValidateCode': str(req_arg['verification_code']),
        'drpLoginType': 1,
        '__ASYNCPOST': 'true',
    }
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

    new_info = urlencode({**cookie_dict, **info})  # 合并两个dict#合并两个dict
    _ = requests.post(master_certif_url, proxies=remote_proxy,
                      data=new_info, headers=header, cookies=my_cookies)
    name_html = requests.get(master_sex_name_url, proxies=remote_proxy, cookies=my_cookies)

    try:

        re_name = re.compile(r'姓名\s*</td>\s*<td.*?>\s*(\S*)\s*</td>')
        re_sex = re.compile(r'性别\s*</td>\s*<td.*?>\s*(\S*)\s*</td>')

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
            success.info = 'user_id:' + req_arg['user_id'] + "," + \
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


def master_get(user_id: str, school_id: str, remote_or_local: bool) -> dict:
    remote_proxy = None
    if remote_or_local:
        remote_proxy_obj = RemoteProxy.query.filter_by(schoolId=school_id).first()
        remote_proxy = {
            "http": remote_proxy_obj.remoteProxy,
            "https": remote_proxy_obj.remoteProxy
        }

    s = requests.session()
    header = {
        'Host': 'yjssys.snnu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.103 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1'}
    html = s.get(master_code_url, proxies=remote_proxy, headers=header)
    my_cookie = html.cookies.get('ASP.NET_SessionId')
    cookie_dict = dict(html.cookies)
    from app import OS_PATH
    img_local_url = "/static/snnu/" + str(user_id) + '.jpg'
    img_name = OS_PATH + img_local_url

    if get_img(proxies=remote_proxy, img_name=img_name, my_cookies=cookie_dict, url=master_code_url):
        # 获取csrf_token
        html = s.get(master_main_url, proxies=remote_proxy, headers=header, cookies=cookie_dict)

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
                user_id),
            current_app.config['COOKIE_LIVE_TIME'],
            json.dumps(cookie_dict))
        result_dict = {
            'user_id': user_id,
            'img_url': current_app.config['IMG_NET_PREFIX'] + img_local_url
        }
    else:
        raise OverflowError
    return result_dict


# get时的占位func,可以返回占位验证码


def place_holder(req_args, school_id):
    return {'error': 1}


# re_schoolNumb = re.compile("学号\s*</td>\s*<td.*?>\s*(\S*)\s*?</td>")
# sex_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[2]/td[2]//text()'
# name_xpath = '//html/body/form/div[2]/table[@class="tbline"]/tr[1]/td[4]//text()'
#
# tree = etree.HTML(name_html.text)
# sex = tree.xpath(sex_xpath)
# name = tree.xpath(name_xpath)
# name_fin = str(name[0]).strip()
# sex_fin = str(sex[0]).strip()
    # if check_token(req_args.get('token')):
    #     if check_remoteOrLocal(school_id):
    #         if check_alive(school_id, alive_redis):
    #             # 发起内网请求，失败后报错，通知管理员
    #             with try_remote(req_args=req_args, school_id=school_id, remote_func=remote_get,
    #                             get_func=place_holder, res_dict=res_dict):
    #                 pass
    #         else:
    #             # todo 外网请求
    #             with try_local(req_args=req_args, school_id=school_id, get_func=place_holder,
    #                            local_func=local_get, res_dict=res_dict):
    #                 pass
    #             # todo 内网未连接，通知管理员，可以返回占位img
    #             # 设置成外网认证
    #             with db.auto_commit():  # 数据库切换成外网
    #                 record = School.query.get(int(school_id))
    #                 record.remote = False
    #
    #     else:
    #         # todo 外网请求
    #         with try_local(req_args=req_args, school_id=school_id, get_func=place_holder,
    #                        local_func=local_get, res_dict=res_dict):
    #             pass
    # else:
    #     abort(400)


# @snnu.route('/change', methods=['POST'])
# @use_small_args()
# def change(args):
#     pass


# # 内网本科认证
# def remote_benke_certif(req_args: dict, url: str, school_id: str) -> dict:
#     r = requests.session()
#     html = r.post(url + '/' + school_abbr + '/certif', json=req_args, data=req_args)
#     try:
#         body = html.text
#         res = json.loads(body)
#     except Exception as e:
#         raise ParamError()  # todo 暂时这么用，因为没做参数校验
#     if res.get('status') != 1:
#         return res
#     else:  # todo 获取头像，存储基本数据
#         get_remote_portrait(img_url=url + '/' + school_abbr + '/protrait/' + str(req_args['user_id']) + '.jpg',
#                             user_id=req_args['user_id'], school_abbr=school_abbr)
#         with db.auto_commit():
#             success = Success()
#             success.schoolId = int(school_id)
#             success.portraitUri = "/static/snnu/portrait/" + \
#                                   str(req_args['user_id']) + '.jpg'
#             success.info = 'name:' + res.get('name') + ',' + 'school_numb:' + str(res.get('school_numb')) + ',' + \
#                            'sex:' + res.get('sex') + ',' + 'identity:1'
#             db.session.add(success)
#     return res
#
#
# # 内网研究生认证
# def remote_master_certif(req_args: dict, url: str, school_id: str) -> dict:
#     r = requests.session()
#     html = r.post(url + '/' + school_abbr + '/certif', json=req_args, data=req_args)
#     try:
#         body = html.text
#         res = json.loads(body)
#     except Exception as e:
#         raise ParamError()  # todo 暂时这么用，因为没做参数校验
#     if res.get('status') != 1:
#         return res
#     else:  # todo 获取头像，存储基本数据
#         get_remote_portrait(img_url=url + '/' + school_abbr + '/protrait/' + str(req_args['user_id']) + '.jpg',
#                             user_id=req_args['user_id'], school_abbr=school_abbr)
#         with db.auto_commit():
#             success = Success()
#             success.schoolId = int(school_id)
#             success.portraitUri = "/static/snnu/portrait/" + \
#                                   str(req_args['user_id']) + '.jpg'
#             success.info = 'name:' + res.get('name') + ',' + 'school_numb:' + str(res.get('school_numb')) + ',' + \
#                            'sex:' + res.get('sex') + ',' + 'identity:2'
#             db.session.add(success)
#     return res


# # 内网本科生验证码
# def remote_benke_get(req_args: dict, url: str) -> dict:
#     r = requests.session()
#     html = r.post(url + '/' + school_abbr + '/get', json=req_args, data=req_args)
#     try:
#         body = html.text
#         res = json.loads(body)
#     except Exception as e:
#         raise ParamError()  # 暂时这么用，因为没做参数校验
#     res['img_url'] = swap_remote_image(img_url=res['img_url'], user_id=req_args['user_id'],
#                                        school_abbr=school_abbr)
#     return res
#
#
# # 内网研究生验证码
# def remote_master_get(req_args: dict, url: str) -> dict:
#     r = requests.session()
#     html = r.post(url + '/' + school_abbr + '/get', json=req_args, data=req_args)
#     try:
#         body = html.text
#         res = json.loads(body)
#     except Exception as e:
#         raise ParamError()  # 暂时这么用，因为没做参数校验
#     res['img_url'] = swap_remote_image(img_url=res['img_url'], user_id=req_args['user_id'],
#                                        school_abbr=school_abbr)
#     return res

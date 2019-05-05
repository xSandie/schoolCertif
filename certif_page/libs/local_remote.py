import json
from contextlib import contextmanager


# 判断内网服务器是否存活
from flask import current_app
from requests import RequestException

from certif_page.libs.cache import cache
from certif_page.models.School import School
from certif_page.models.base import db


def check_alive(school_abbr: str, alive_redis):
    try:
        record = json.loads(alive_redis.get(
            current_app.config['REMOTE_ALIVE_PREFIX']+school_abbr))
        if record.alive:
            return True
        else:
            return False
    except Exception as e:
        return False  # 内存中不存在


@contextmanager
def try_local(
    *,
    req_args: dict,
    school_id: str,
    get_func: function,
    local_func: function,
        res_dict: dict):
    # todo 发起外网请求失败后，发起内网请求
    try:
        yield
        res_dict.update({**local_func(req_args, school_id)})  # todo 传参，调发起外网请求
    except Exception as e:
        # todo 外网请求失败
        if isinstance(e, (ConnectionError, RequestException)):
            # todo 网址挂了通知管理员，设置外网不可用投票，
            # todo 检查票数，并设置相应外网可用状态
            pass
        elif isinstance(e, (OverflowError,)):
            # todo 存储异常记录日志通知管理员
            pass
        elif isinstance(e, (IndexError,)):
            # todo 可能是网页结构改变记录的投票,或者账号密码错误，进行计数错误出现太多次可能就是网页结构改变，通知管理员
            res_dict.clear()
            res_dict.update({**get_func(req_args, school_id)})
            res_dict['status'] = 0
            from certif_page.libs.redis_conn import alive_redis
            alive_redis.incr('prob:'+school_id)
            if int(alive_redis.get('prob:'+school_id)>current_app.config['ALERT_THRESHOLD']):
                #todo 邮件通知管理员
                pass
            # key为name的value增值操作，默认1，key不存在则被创建并设为amount
        else:
            # todo 通知管理员，未知异常
            raise e


@contextmanager
def try_remote(
    *,
    req_args: dict,
    school_id: str,
    remote_func: function,
        res_dict: dict):
    # todo 尝试内网请求
    try:
        res_dict.update({**remote_func(req_args, school_id)})  # todo 传参
    except Exception as e:
        if isinstance(e, (ConnectionError, RequestException)):
            # todo 网址挂了通知管理员
            with db.auto_commit():#数据库切换成外网
                record = School.query.get(int(school_id))
                record.remote = False
        else:
            # todo 通知管理员，未知异常
            raise e

# 每十分钟，确认一次是通过内网还是通过外网
@cache.memoize(600)
def check_remoteOrLocal(school_id: str) -> bool:
    # todo 检查数据库 是通过外网请求还是通过内网，默认通过外网
    # 外网存活返回False
    record = School.query.get(int(school_id))
    if record.remote:
        return True  # 通过内网
    else:
        return False  # 通过外网

# # 检查出错原因
# def check_fail_reason(res_dict, get_func:function,req_args:dict):
#     try:
#         status = int(res_dict.get('status'))
#         if status == 3:# cookie过期，或不存在
#             pass
#         elif status == 2:# 网址无法访问，或存储图片失败
#             # 联系客服的提示
#             pass
#         elif status == 0:# 账号密码错误，直接返回0, 重新调用get
#
#     except Exception as e:
#         # 未知错误未返回状态码
#         pass

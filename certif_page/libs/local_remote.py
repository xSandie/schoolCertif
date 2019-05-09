import json
from contextlib import contextmanager


# 判断内网服务器是否存活
from flask import current_app
from requests import RequestException

from certif_page.libs.CertifErrors.ParamError import ParamError
from certif_page.libs.cache import cache
from certif_page.models.School import School
from certif_page.models.base import db


def check_alive(school_id:str,alive_redis):
    try:
        record = json.loads(alive_redis.get(
            current_app.config['REMOTE_ALIVE_PREFIX']+school_id))
        if record.get('alive'):
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
    get_func,
    local_func,
        res_dict: dict):
    try:
        yield
        res_dict.update({**local_func(req_args, school_id)})  # todo 传参，调发起外网请求
    except Exception as e:
        # todo 外网请求失败
        if isinstance(e, (ConnectionError, RequestException)):
            # todo 网址挂了通知管理员
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
            if int(alive_redis.get('prob:'+school_id))>current_app.config['ALERT_THRESHOLD']:
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
    remote_func,
        get_func,
        res_dict: dict):
    # todo 尝试内网请求
    from certif_page.libs.redis_conn import alive_redis
    try:
        yield
        res_dict.update({**remote_func(req_args, school_id)})  # todo 传参
    except Exception as e:
        if isinstance(e, (ParamError,)):
            #参数错误
            pass
        elif isinstance(e, (ConnectionError, RequestException)):
            # todo 网址挂了通知管理员
            with db.auto_commit():  # 数据库切换成外网
                record = School.query.get(int(school_id))
                record.remote = False
            # 设置网址不可用
            record = json.loads(alive_redis.get(
                current_app.config['REMOTE_ALIVE_PREFIX'] + school_id))
            record['alive'] = False
            dic = json.dumps(record)
            alive_redis.setex("remote:" + str(school_id), 900, dic)
            pass
        elif isinstance(e, (IndexError,)):
            # todo 可能是网页结构改变记录的投票,或者账号密码错误，进行计数错误出现太多次可能就是网页结构改变，通知管理员
            res_dict.clear()
            res_dict.update({**get_func(req_args, school_id)})
            res_dict['status'] = 0
            alive_redis.incr('remoteProb:' + school_id)
            if int(alive_redis.get('remoteProb:' + school_id)) > current_app.config['ALERT_THRESHOLD']:
                # todo 远端网址挂了，邮件通知管理员
                pass
        else:
            # todo 通知管理员，记录未知异常
            with db.auto_commit():  # 数据库切换成外网
                record = School.query.get(int(school_id))
                record.remote = False
            # 设置网址不可用
            record = json.loads(alive_redis.get(
                current_app.config['REMOTE_ALIVE_PREFIX'] + school_id))
            record['alive']=False
            dic = json.dumps(record)
            alive_redis.setex("remote:" + str(school_id), 900, dic)



# 每十分钟，确认一次是通过内网还是通过外网
@cache.memoize(60)#todo 上线前修改
def check_remoteOrLocal(school_id: str) -> bool:
    # todo 检查数据库 是通过外网请求还是通过内网，默认通过外网
    # 外网存活返回False
    record = School.query.get(int(school_id))
    if record.remote:
        return True  # 通过内网
    else:
        return False  # 通过外网
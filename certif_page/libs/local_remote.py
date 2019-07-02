# 判断内网服务器是否存活
import json
from flask import current_app

from certif_page.config.setting import RedisTime
from certif_page.libs.cache import cache
from certif_page.models.School import School


def check_alive(school_id: str, alive_redis):
    try:
        record = json.loads(alive_redis.get(
            current_app.config['REMOTE_ALIVE_PREFIX'] + school_id))
        if record.get('alive'):
            return True
        else:
            return False
    except Exception as e:
        return False  # 内存中不存在


# 每十分钟，确认一次是通过内网还是通过外网
@cache.memoize(RedisTime.check_remote_or_local)  # todo 上线前修改
def check_remoteOrLocal(school_id: str) -> bool:
    # todo 检查数据库 是通过外网请求还是通过内网，默认通过外网
    # 外网存活返回False
    record = School.query.get(int(school_id))
    if record.remote:
        return True  # 通过内网
    else:
        return False  # 通过外网

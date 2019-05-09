from certif_page.libs.redis_conn import token_redis
from certif_page.models.Token import Token

#todo 检查是否还能请求
def check_token(token:str)->bool:
    prefix = 'token:'
    r_token = token_redis.get(prefix + token)
    if not r_token:
        #内存中不存在，今天第一次请求
        token_obj = Token.query.filter_by(value=token).first()
        token_redis.setex(prefix+token_obj.value,86400,token_obj.limitPerDay)#默认二十四小时
        return True
    elif r_token and int(r_token)>0:
        token_redis.decr(prefix+token, 1)
        return True
    else:
        #todo 加入发送邮件通知逻辑
        return False
 
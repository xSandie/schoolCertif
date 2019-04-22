import redis
cookie_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)#cookie存到1号数据库
remoteUrl_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)#存内网网址，键为学校缩写
alive_redis =  redis.StrictRedis(host='127.0.0.1', port=6379, db=3)#内网存活状态
token_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)#token与剩余次数数据库

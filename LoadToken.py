'''Token每日重新加载'''
import redis

token_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)#token与剩余次数数据库

token_redis.flushdb()

 
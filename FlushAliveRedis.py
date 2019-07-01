'''每日0点flush alive_redis'''
import redis

alive_redis =  redis.StrictRedis(host='127.0.0.1', port=6379, db=3)#内外网存活状态
alive_redis.flushdb()
 
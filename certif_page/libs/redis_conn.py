import redis
cookie_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=1)#cookie存到1号数据库
# remoteUrl_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=2)#存内网网址，键为学校缩写
alive_redis =  redis.StrictRedis(host='127.0.0.1', port=6379, db=3)#内外网存活状态
token_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=4)#token与剩余次数数据库

#数据结构
# token_redis={
# 'token:值':'次数'
# }

# alive_redis={
#     "remote:学校缩写":{
#         'alive':True,
#         'url':'http://127.0.0.1:6001'
#     }
# }

# 可能是网页结构改变记录的投票
# alive_redis ={
#     'prob:学校id':'票数'
# }

# cookie_redis={
#     '学校id:用户id':cookie_dict
# }



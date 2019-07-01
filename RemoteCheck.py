"""认证内网端口及地址数据库，内网存活测试"""

# 连接数据库
import datetime
import json

import pymysql
import redis
import requests
from requests import RequestException

alive_redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)  # 内外网存活状态
connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='x12345678',
    db='certif',
    charset='utf8'
)

cursor = connect.cursor()
query_sql = "SELECT * FROM remote_url"
cursor.execute(query_sql)
all_urls = cursor.fetchall()

for url in all_urls:
    (_, _, remote_url, school_id) = url
    try:
        r = requests.session()
        html = r.get(remote_url + '/')
        if html.status_code == 200:
            dic = json.dumps({
                'alive': True,
                'url': remote_url
            })
        else:
            raise ConnectionError
    except Exception as e:
        if isinstance(e, (ConnectionError, RequestException)):
            # 内网断连
            pass
        else:
            # todo 通知管理员或者记录日志
            pass
        dic = json.dumps({
            'alive': False,
            'proxy': remote_url
        })

    alive_redis.setex("remote:" + str(school_id), 900, dic)  # 存活15分钟
    print('------------------------------')
    print('schoolId:' + str(school_id))  # todo delete
    print('status:' + str(json.loads(dic)))  # todo delete
    print(datetime.datetime.now())
    print('-----------------------------')

connect.commit()
cursor.close()
connect.close()

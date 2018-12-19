#帮助设置文件路径及网络地址
from app import OS_PATH

img_local_prefix="/static/"
# img_net_prefix='http://api.inschool.tech'
img_net_prefix='http://127.0.0.1:4000'

img_local_url=OS_PATH+img_local_prefix #~/static/
#本地图片地址

img_net_url_prefix=img_net_prefix+img_local_prefix #http://127.0.0.1:5000 /static/
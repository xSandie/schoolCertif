import os

import requests
from flask import current_app
from app import OS_PATH

# 将内网的图片转到外网上来，并返回外网地址
def swap_remote_url(*, img_url, user_id, school_abbr) -> str:
    s = requests.session()
    img = requests.get(img_url)
    img_name = OS_PATH + "/static/" + school_abbr + "/" + str(user_id) + '.jpg'
    with open(img_name, 'wb') as f:
        f.write(img.content)
    return current_app.config['IMG_NET_PREFIX'] + img_name


# 外网获取图片并存储
def get_img(*, img_name, my_cookies, url):
    img_get = requests.get(url, cookies=my_cookies)
    try:
        with open(img_name, 'wb') as f:
            f.write(img_get.content)
        return True
    except Exception as _:
        return False


# 重命名认证成功后的二维码图片
def rename_code(*, pic_name, user_id, school_abbr):
    save_loop = True
    count = 0
    while(save_loop):
        try:
            old_pic_loc = OS_PATH + '/static/' + \
                school_abbr + '/' + str(user_id) + '.jpg'
            new_pic_name = OS_PATH + '/static/' + school_abbr + '/' + \
                str(pic_name) + '(' + str(user_id) + str(count) + ')' + '.jpg'
            os.rename(old_pic_loc, new_pic_name)
            # 改名成功就跳出循环
            save_loop = False
        except Exception as _:
            count += 1
            if(count >= 50):
                return False  # 致命死循环
    return True

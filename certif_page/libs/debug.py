import requests

# todo 临时切回本地进行debug
def debug(req_args, debug_url, school_abbr) -> dict:
    if req_args.get('account'):  # 是认证
        r = requests.session()
        html = r.get(
            debug_url +
            '/' +
            school_abbr +
            '/certif',
            json=req_args,
            data=req_args)
        return html.content
    else:  # 是获取验证码
        r = requests.session()
        html = r.get(
            debug_url +
            '/' +
            school_abbr +
            '/get',
            data=req_args,
            json=req_args)
        return html.content

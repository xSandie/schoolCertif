# 少量参数直接解包

import functools
from webargs.flaskparser import parser


class Parser(object):
    def __call__(self, schema):
        def wrapper(func):
            @functools.wraps(func)
            def decorator(self):
                # 校验参数
                req_args = parser.parse(schema, self.request)
                # 参数个数在5个以内，直接解构
                if len(req_args) <= 5:
                    # 去掉只是用于算次数和校验的token
                    if "token" in req_args.keys():
                        req_args.pop("token")
                    return func(self, **req_args)

                return func(self, req_args)

            return decorator

        return wrapper


use_small_args = Parser()

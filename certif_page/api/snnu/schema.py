# webargs前端需要传的参数
from webargs import fields
from certif_page.libs.token import check_token


class GetSchema():
    token = fields.Str(required=True, validate=check_token, description="认证token"),
    user_id = fields.Str(required=True, description="用户id")


# get_schema = {
#     "token": fields.Str(required=True, validate=check_token, description="认证token"),
#     "user_id": fields.Str(required=True, description="用户id")
# }

class CertifSchema():
    token = fields.Str(required=True, validate=check_token, description="认证token"),
    user_id = fields.Str(required=True, description="用户id"),
    account = fields.Str(required=True, description="账号"),
    password = fields.Str(required=True, description="密码"),
    verification_code = fields.Str(required=True, description="验证码")

# certif_schema = {
#     "token": fields.Str(required=True, validate=check_token, description="认证token"),
#     "user_id": fields.Str(required=True, description="用户id"),
#     "account": fields.Str(required=True, description="账号"),
#     "password": fields.Str(required=True, description="密码"),
#     "verification_code": fields.Str(required=True, description="验证码")
# }

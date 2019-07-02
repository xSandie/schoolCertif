# webargs前端需要传的参数
from webargs import fields

from certif_page.config.setting import UserStatus, AdminPermission
from certif_page.libs.token import check_token
from certif_page.models.Admin import Admin


def check_admin_account(account):
    admin = Admin.query.filter_by(account=account).first()
    if admin.status == UserStatus.normal and admin.permissions > AdminPermission.team:
        return True
    return False


class GetSchema():
    token = fields.Str(required=True, validate=check_token, description="认证token"),
    user_id = fields.Str(required=True, description="用户id")
    identity = fields.Int(required=True, validate=lambda i: i in [1, 2], description="用户身份 1为本科生 2为研究生")


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
    identity = fields.Int(required=True, validate=lambda i: i in [1, 2], description="用户身份 1为本科生 2为研究生")


# certif_schema = {
#     "token": fields.Str(required=True, validate=check_token, description="认证token"),
#     "user_id": fields.Str(required=True, description="用户id"),
#     "account": fields.Str(required=True, description="账号"),
#     "password": fields.Str(required=True, description="密码"),
#     "verification_code": fields.Str(required=True, description="验证码")
# }


class ChangeSchema():
    account = fields.Str(required=True, validate=check_admin_account, description="管理员用户名"),
    password = fields.Str(required=True, description="密码"),

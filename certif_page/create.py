# -*- coding:utf-8 -*- 
from flask import Flask
from flask_migrate import Migrate

from certif_page.models.base import db


def register_blueprints(app):#注册蓝图
    from certif_page.api.snnu.certif import snnu
    app.register_blueprint(snnu, url_prefix='/snnu')


def create_app():
    app=Flask(__name__)#不要漏掉本函数参数
    app.config.from_object('certif_page.config.setting')
    app.config.from_object('certif_page.config.secure')
    #上面进行基本配置
    register_blueprints(app)
    db.init_app(app)

    migrate=Migrate(app,db)
    with app.app_context():
        db.create_all()

    return app #一定要记得返回创建的核心对象app
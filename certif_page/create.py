# -*- coding:utf-8 -*- 
import datetime
import hashlib
import os

import click
from flask import Flask
from flask_migrate import Migrate

from certif_page.config.setting import config
from certif_page.libs.args_and_docs.ApiDoc import FlaskApiDoc
from certif_page.libs.cache import cache
from certif_page.models.Token import Token
from certif_page.models.base import db


def register_blueprints(app):  # 注册蓝图
    from certif_page.api.snnu.certif import snnu
    app.register_blueprint(snnu, url_prefix='/snnu')


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')
    app = Flask(__name__)  # 不要漏掉本函数参数
    app.config.from_object(config[config_name])
    # 上面进行基本配置
    register_blueprints(app)
    db.init_app(app)
    cache.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()

    register_shell_context(app)
    register_commands(app)

    app.config['API_DOC_MEMBER'] = ['snnu',]
    FlaskApiDoc(app=app)
    return app  # 一定要记得返回创建的核心对象app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app, db=db)


def register_commands(app):
    @app.cli.command('initdb')
    def initdb():
        click.echo("Initializing the database")
        with app.app_context():
            db.drop_all()
            db.create_all()
        click.echo("Done")

    @app.cli.command('gentoken')  # todo 带参数limit
    def gen_token():
        click.echo("Initializing token")
        this_time = str(int(datetime.datetime.now().timestamp()))
        md5 = hashlib.md5()
        i = 0  # 线性探测
        while True:
            md5.update((this_time + str(i)).encode('utf-8'))
            test_token = md5.hexdigest()
            token_exist = Token.query.filter_by(value=test_token).first()

            if token_exist is None:  # 数据库 不存在重复值
                break
            i += 1
        with app.app_context():
            with db.auto_commit():
                token_obj = Token()
                token_obj.value = test_token
                db.session.add(token_obj)
        click.echo(test_token)

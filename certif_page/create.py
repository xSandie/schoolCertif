# -*- coding:utf-8 -*- 
import click
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

    register_shell_context(app)
    register_commands(app)

    return app #一定要记得返回创建的核心对象app

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(app=app,db=db)

def register_commands(app):
    @app.cli.command('initdb')
    def initdb():
        click.echo("Initializing the database")
        with app.app_context():
            db.drop_all()
            db.create_all()
        click.echo("Done")
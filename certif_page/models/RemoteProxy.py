from certif_page.models.base import Base, db


class RemoteProxy(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    remoteProxy = db.Column(db.String(30), nullable=False)  # 带端口号的http地址 无/结尾
    port = db.Column(db.String(7), nullable=False)  # 端口
    school = db.relationship('School', back_populates='proxy')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)

    # 存活数据库dict
    # key:schoolId
    # value:{
    #     url:str
    #     alive:bool
    # }

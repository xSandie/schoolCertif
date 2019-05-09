from certif_page.models.base import Base, db


class RemoteUrl(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(30), nullable=False)#带端口号的http地址 /结尾

    school = db.relationship('School', back_populates='remoteUrl')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)

    # 存活数据库dict
    # key:schoolId
    # value:{
    #     url:str
    #     alive:bool
    # }
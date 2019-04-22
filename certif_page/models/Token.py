from certif_page.models.base import Base, db


class Token(Base):
    id = db.Column(db.BigInteger,primary_key=True, autoincrement=True)
    value = db.Column(db.String(140), index=True, nullable=False)
    limitPerDay = db.Column(db.Integer,default=80000)#日限额，默认300000次一天
    status = db.Column(db.SmallInteger,default=1)#正常
    permission = db.Column(db.SmallInteger,default=0)#0 无查看头像权限 1 有查看头像权限
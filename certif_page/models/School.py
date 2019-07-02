from certif_page.models.base import Base, db


class School(Base):
    schoolId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schoolName = db.Column(db.String(40), nullable=False, unique=True)
    schoolAbbr = db.Column(db.String(10), nullable=False)

    proxy = db.relationship('RemoteProxy', back_populates='school')
    admins = db.relationship('Admin', back_populates='school')
    successPeople = db.relationship('Success', back_populates='school')
    remote = db.Column(db.Boolean, default=False)  # 默认不使用内网

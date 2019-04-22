from certif_page.models.base import Base, db


class RemoteUrl(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(20), nullable=False)#带端口号的http地址

    school = db.relationship('School', back_populates='remoteUrl')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)
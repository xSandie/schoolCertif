from certif_page.config.setting import UserStatus, AdminPermission
from certif_page.models.base import db, Base


class Admin(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(20), nullable=False, unique=True, index=True)
    password = db.Column(db.String(20), nullable=False)

    permissions = db.Column(db.Integer, default=AdminPermission.team)
    status = db.Column(db.String(10), default=UserStatus.normal)

    school = db.relationship('School', back_populates='admins')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)

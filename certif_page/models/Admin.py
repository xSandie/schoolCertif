from certif_page.models.base import db, Base


class Admin(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)

    school = db.relationship('School', back_ref='admins')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)

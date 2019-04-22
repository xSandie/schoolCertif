from certif_page.models.base import Base, db


class Success(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school = db.relationship('School', back_populates='successPeople')
    schoolId = db.Column(db.Integer, db.ForeignKey('school.schoolId'), nullable=False)

    portraitUri = db.Column(db.String(50))
    info = db.Column(db.Text)
    userId = db.Column(db.Integer)
 
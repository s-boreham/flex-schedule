from db import db

class TeacherModel(db.Model):
    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(80), nullable=False)
    lName = db.Column(db.String(80), nullable=False)
    instrument = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    teaching_hours = db.relationship("TeachingHourModel", back_populates="teacher", lazy="dynamic")
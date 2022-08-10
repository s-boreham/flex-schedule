from db import db

class TeachingHourModel(db.Model):
    __tablename__ = "teaching_hour"

    id = db.Column(db.Integer, primary_key=True)
    dayOfWeek = db.Column(db.String(80), nullable=False)
    opens = db.Column(db.String(80), nullable=False)
    closes = db.Column(db.String(80), nullable=False)
    validFrom = db.Column(db.String(80), nullable=False)
    validThrough = db.Column(db.String(80), nullable=False)

    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), unique=False, nullable=False
    )
    teacher = db.relationship("TeacherModel", back_populates="teaching_hours")

    def get_valid_teacher_hours_ordered(teacher_id, date):
        return TeachingHourModel.query.filter(
                TeachingHourModel.teacher_id == teacher_id,
                TeachingHourModel.validThrough >= date
            ).order_by(TeachingHourModel.validFrom)
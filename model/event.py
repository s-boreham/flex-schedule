from db import db

class EventModel(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), unique=False, nullable=False
    )
    date = db.Column(db.String(80), nullable=False)
    timeStart = db.Column(db.String(80), nullable=False)
    timeEnd = db.Column(db.String(80), nullable=False)
    eventType = db.Column(db.String(80), default="Lesson")

    def get_teacher_events_from_date(teacher_id, startDate):
        return EventModel.query.filter(
                    EventModel.date >= startDate, 
                    EventModel.teacher_id == teacher_id
                ).order_by(
                    EventModel.date, 
                    EventModel.timeStart
                )
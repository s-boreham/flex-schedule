from datetime import date

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from schema.event import EventSchema
from model.event import EventModel
from model.teaching_hours import TeachingHourModel

from sqlalchemy.exc import SQLAlchemyError
from db import db

blp = Blueprint("Events", "events", description="Operations on lessons and other events")


@blp.route("/teacher/<int:teacher_id>/event/<int:event_id>")
class Teacher(MethodView):

    @jwt_required()
    @blp.response(200, EventSchema(exclude=("teacher_id", "id",)))
    def get(cls, teacher_id, event_id):
        event = EventModel.query.get_or_404(event_id)

        return event

    @jwt_required()
    @blp.arguments(EventSchema)
    @blp.response(200, EventSchema(exclude=("teacher_id", "id",)))
    def put(cls, event_data, teacher_id, event_id):
        event = EventModel.query.get_or_404(event_id)

        event_data["teacher_id"] = teacher_id
        update_event = EventModel(**event_data)

        if update_event.timeStart > update_event.timeEnd:
            abort (400, message="Event ends earlier than it begins.")

        # inside valid teaching hours?
        weekDay = date.fromisoformat(update_event.date).strftime("%A")
        validHours = TeachingHourModel.query.filter(
            TeachingHourModel.teacher_id==teacher_id,
            TeachingHourModel.dayOfWeek==weekDay, 
            TeachingHourModel.validFrom<=update_event.date, 
            TeachingHourModel.validThrough>=update_event.date
        ).first()
        if not (validHours.opens <= update_event.timeStart and validHours.closes >= update_event.timeEnd):
            abort(400, message="Event must not exceed teaching hours.")

        # no overlap with other events?
        for e in EventModel.query.filter(EventModel.id != event.id, EventModel.date == update_event.date).all():
            if not (update_event.timeStart >= e.timeEnd or update_event.timeEnd <= e.timeStart):
                abort(400, message="Event overlaps with at least one existing event.")


        event.date = update_event.date
        event.timeStart = update_event.timeStart
        event.timeEnd = update_event.timeEnd

        if "eventType" in event_data:
            event.eventType = update_event.eventType


        try:
            db.session.add(event)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="There was an error updating the event.")

        return event

    @jwt_required()
    @blp.response(200)
    def delete(cls, teacher_id, event_id):
        event = EventModel.query.get_or_404(event_id)

        try:
            db.session.delete(event)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="There was an error deleting the event.")

        return "Event deleted."

@blp.route("/teacher/<int:teacher_id>/events")
class TeacherList(MethodView):

    @jwt_required()
    @blp.response(200, EventSchema(many=True, exclude=("teacher_id",)))
    def get(cls, teacher_id):
        return EventModel.query.filter_by(teacher_id=teacher_id)

    @jwt_required()
    @blp.arguments(EventSchema)
    @blp.response(201, EventSchema)
    def post(cls, event_data, teacher_id):
        event_data["teacher_id"] = teacher_id
        event = EventModel(**event_data)

        if event.timeStart > event.timeEnd:
            abort (400, message="Event ends earlier than it begins.")
        
        # inside valid teaching hours?
        weekDay = date.fromisoformat(event.date).strftime("%A")
        validHours = TeachingHourModel.query.filter(
            TeachingHourModel.dayOfWeek==weekDay, 
            TeachingHourModel.validFrom<=event.date, 
            TeachingHourModel.validThrough>=event.date
        ).first()
        if not (validHours.opens <= event.timeStart and validHours.closes >= event.timeEnd):
            abort(400, message="Event must not exceed teaching hours.")

        # no overlap with other events?
        for e in EventModel.query.filter_by(date=event.date).all():
            if not (event.timeStart >= e.timeEnd or event.timeEnd <= e.timeStart):
                abort(400, message="Event overlaps with at least one existing event.")

        try:
            db.session.add(event)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="There was an error saving the event.")
        

        return event
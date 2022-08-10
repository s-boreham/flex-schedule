from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from schema.teaching_hours import TeachingHourSchema
from model.teaching_hours import TeachingHourModel

from sqlalchemy.exc import SQLAlchemyError
from db import db

blp = Blueprint("Hours", "hours", description="Operations on teaching hours")

@blp.route("/teacher/<int:teacher_id>/schedule/<int:hours_spec_id>")
class schedule(MethodView):

    @jwt_required()
    @blp.arguments(TeachingHourSchema(exclude=("dayOfWeek",), partial=("opens", "closes", "validFrom", "validThrough")))
    @blp.response(200, TeachingHourSchema(exclude=("teacher_id",)))
    def put(cls, hours_data, teacher_id, hours_spec_id):
        hours_spec = TeachingHourModel.query.get_or_404(hours_spec_id)

        if "validFrom" and "validThrough" in hours_data:
            # validate valid dates args
            if hours_data["validFrom"] > hours_data["validThrough"]:
                abort (400, message="Invalid valid dates.")

            # check for existing hours with same weekday with overlapping valid dates
            overlapExists = TeachingHourModel.query.filter(
                TeachingHourModel.id != hours_spec_id,
                TeachingHourModel.dayOfWeek == hours_spec.dayOfWeek,
                TeachingHourModel.validFrom <= hours_data["validThrough"],
                TeachingHourModel.validThrough >= hours_data["validFrom"]
            ).first()
            if overlapExists:
                abort(400, message=overlapExists)

            hours_spec.validFrom = hours_data["validFrom"]
            hours_spec.validThrough = hours_data["validThrough"]


        if "opens" and "closes" in hours_data:
            # validate opening hours args
            if hours_data["opens"] > hours_data["closes"]:
                abort(400, message="Invalid opening hours")

            hours_spec.opens = hours_data["opens"]
            hours_spec.closes = hours_data["closes"]


        try:
            db.session.add(hours_spec)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured updating the schedule.")

        return hours_spec

    @jwt_required()
    @blp.response(200)
    def delete(cls, teacher_id, hours_spec_id):
        hours_spec = TeachingHourModel.query.get_or_404(hours_spec_id)

        try:
            db.session.delete(hours_spec)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured deleting the teaching hour specification.")

        return "Hour specification deleted."


@blp.route("/teacher/<int:teacher_id>/schedule")
class ScheduleList(MethodView):
    @blp.response(200, TeachingHourSchema(many=True, exclude=("teacher_id",)))
    def get(cls, teacher_id):
        return TeachingHourModel.query.filter_by(teacher_id=teacher_id)

    @jwt_required()
    @blp.arguments(TeachingHourSchema)
    @blp.response(201, TeachingHourSchema)
    def post(cls, hours_data, teacher_id):

        # validate args
        if hours_data["validFrom"] > hours_data["validThrough"]:
            abort (400, message="Invalid valid dates.")

        # check for existing hours with same weekday with overlapping valid dates
        overlapExists = TeachingHourModel.query.filter(
            TeachingHourModel.dayOfWeek == hours_data["dayOfWeek"],
            TeachingHourModel.validFrom <= hours_data["validThrough"],
            TeachingHourModel.validThrough >= hours_data["validFrom"]
        ).first()
        if overlapExists:
            abort(400, message=overlapExists)

        # create new teaching hours specification
        hours_data["teacher_id"] = teacher_id
        hours = TeachingHourModel(**hours_data)

        try:
            db.session.add(hours)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured saving the teaching hours specification.")
        

        return hours
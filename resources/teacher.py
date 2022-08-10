from werkzeug.security import check_password_hash

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import create_access_token, jwt_required

from schema.teacher import TeacherSchema
from model.teacher import TeacherModel

from sqlalchemy.exc import SQLAlchemyError
from db import db

blp = Blueprint("Teachers", "teachers", description="Operations on teachers")

@blp.route("/teacher/<int:teacher_id>")
class Teacher(MethodView):
    @jwt_required()
    @blp.response(200, TeacherSchema(exclude=("id", )))
    def get(cls, teacher_id):
        teacher = TeacherModel.query.get_or_404(teacher_id)

        return teacher


@blp.route("/teachers/")
class TeacherList(MethodView):
    @jwt_required()
    @blp.response(200, TeacherSchema(many=True, only=("fName", "lName", "instrument", "password")))
    def get(cls):
        return TeacherModel.query.all()



@blp.route("/teachers/login")
class TeacherLogin(MethodView):
    @blp.arguments(TeacherSchema(only=("email", "password")))
    def post(cls, login_data):
        teacher = TeacherModel.query.filter(
            TeacherModel.email == login_data["email"]
        ).first()

        if teacher and check_password_hash(teacher.password, login_data["password"]):
            access_token = create_access_token(identity=teacher.id)
            return {"access_token": access_token}, 200

        abort(401, message="Invalid credentials.")
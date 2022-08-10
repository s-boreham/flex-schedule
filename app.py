import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from flask import Flask
from flask_smorest import Api, abort
from flask_jwt_extended import JWTManager

from db import db
from sqlalchemy.exc import SQLAlchemyError

import model

from resources.teacher import blp as TeacherBlueprint
from resources.schedule import blp as ScheduleBlueprint
from resources.event import blp as EventBlueprint
from resources.availability import blp as AvailabilityBlueprint

load_dotenv()

app = Flask(__name__)

app.config["API_TITLE"] = "Steven Boreham's Lesson Booking API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config[
    "OPENAPI_SWAGGER_UI_URL"
] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

uri = os.environ.get('DATABASE_URL')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config ['JSON_SORT_KEYS'] = False

db.init_app(app)

api = Api(app)

app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()
    if not model.teacher.TeacherModel.query.filter_by(id=1).first():
        admin_data = {
            "fName": os.environ.get('ADMIN_FNAME'),
            "lName": os.environ.get('ADMIN_LNAME'),
            "instrument": os.environ.get('ADMIN_INSTRUMENT'),
            "email": os.environ.get('ADMIN_EMAIL'),
            "password": generate_password_hash(os.environ.get('ADMIN_PASSWORD')),
            "unhashed": os.environ.get('ADMIN_PASSWORD')
        }
        admin = model.teacher.TeacherModel(**admin_data)
        try:
            db.session.add(admin)
            db.session.commit()
        except SQLAlchemyError as e:
                abort(500, message=str(e.__dict__['orig']))
        

api.register_blueprint(TeacherBlueprint)
api.register_blueprint(ScheduleBlueprint)
api.register_blueprint(EventBlueprint)
api.register_blueprint(AvailabilityBlueprint)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
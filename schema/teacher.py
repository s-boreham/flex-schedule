from marshmallow import Schema, fields

class TeacherSchema(Schema):
    id = fields.Int(dump_only=True)
    fName = fields.String(required=True)
    lName = fields.String(required=True)
    instrument = fields.String()    
    email = fields.Email(required=True)
    password = fields.String(load_only=True, required=True)

    class Meta:
        ordered = True
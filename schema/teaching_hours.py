from marshmallow import Schema, fields, validate

class TeachingHourSchema(Schema):
    id = fields.Int(dump_only=True)
    teacher_id = fields.Int()
    dayOfWeek = fields.String(required=True, validate=validate.OneOf(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")))
    opens = fields.String(load_default="")
    closes = fields.String(load_default="")
    validFrom = fields.String(required=True)
    validThrough = fields.String(required=True)

    class Meta:
        ordered = True
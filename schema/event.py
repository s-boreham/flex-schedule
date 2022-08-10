from marshmallow import Schema, fields, validate

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    teacher_id = fields.Int(dump_only=True)
    date = fields.String(required=True)
    timeStart = fields.String(required=True)
    timeEnd = fields.String(required=True)
    eventType = fields.String(load_default="Lesson", validate=validate.OneOf(["Lesson", "Private"]))

    class Meta:
        ordered = True
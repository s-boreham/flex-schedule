from marshmallow import Schema, fields

class QueryArgSchema(Schema):
    year = fields.Int(required=False)
    month = fields.Int(required=False)
    minDuration = fields.Int(required=False)

class AvailableSlotSchema(Schema):
    timeStart = fields.String(dump_only=True)
    timeEnd = fields.String(dump_only=True)
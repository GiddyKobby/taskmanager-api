from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str()  # 👈 added description
    done = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
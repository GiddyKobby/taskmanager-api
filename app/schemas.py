from marshmallow import Schema, fields, validate

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str()  # 👈 added description
    done = fields.Bool()
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "raise"  # Raises error if extra fields are sent
class TaskUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1))
    done = fields.Bool()

    class Meta:
        unknown = "raise" 
        
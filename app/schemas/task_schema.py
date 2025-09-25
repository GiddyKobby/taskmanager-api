from marshmallow import Schema, fields

# 🔹 Schema classes
class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    done = fields.Bool()
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class TaskUpdateSchema(Schema):
    title = fields.Str()
    description = fields.Str()
    done = fields.Bool()

# 🔹 Schema instances (these are what you import in routes)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_update_schema = TaskUpdateSchema()

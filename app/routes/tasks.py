from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task
from ..extensions import db, cache
from ..schemas import TaskSchema

task_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

@task_bp.route('/', methods=['GET'])
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 100)
    cache_key = f"tasks:{user_id}:{page}:{per_page}"
    data = cache.get(cache_key)
    if data:
        return data

    query = Task.query.filter_by(user_id=user_id).order_by(Task.id)
    pag = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'page': page,
        'per_page': per_page,
        'total': pag.total,
        'tasks': tasks_schema.dump(pag.items)
    }
    cache.set(cache_key, result)
    return result


@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    # Validate input with schema
    errors = task_schema.validate(data)
    if errors:
        return {"errors": errors}, 400

    # 👇 include description in task creation
    task = Task(
        title=data['title'],
        description=data.get('description'),  # added
        done=data.get('done', False),
        user_id=user_id
    )

    db.session.add(task)
    db.session.commit()
    cache.clear()  # for demo; in prod, clear user-specific cache keys

    return task_schema.dump(task), 201

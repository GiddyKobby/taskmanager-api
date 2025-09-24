from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task
from ..extensions import db, cache
from marshmallow import ValidationError
from ..schemas import TaskSchema, TaskUpdateSchema

task_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_update_schema = TaskUpdateSchema()

@task_bp.route('/', methods=['GET'])
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()

    # Query params for pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Optional filter by completion status
    done_filter = request.args.get('done')

    query = Task.query.filter_by(user_id=user_id)

    if done_filter is not None:
        if done_filter.lower() in ["true", "1"]:
            query = query.filter_by(done=True)
        elif done_filter.lower() in ["false", "0"]:
            query = query.filter_by(done=False)

    # Keep filtering and add ordering
    query = query.order_by(Task.id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "tasks": tasks_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }
    cache.set(cache_key, result)
    return result


@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    try:
        validated = task_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 422

    task = Task(title=validated['title'], done=validated.get('done', False), user_id=user_id)
    db.session.add(task)
    db.session.commit()
    cache.clear()
    return task_schema.dump(task), 201

# 🔹 GET a single task by ID
@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {"error": "Task not found"}, 404
    return task_schema.dump(task)

# 🔹 UPDATE (PUT/PATCH) a task
@task_bp.route('/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {"error":"Task not found"},404

    data = request.get_json() or {}
    try:
        validated = task_update_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 422

    if "title" in validated:
        task.title = validated["title"]
    if "done" in validated:
        task.done = validated["done"]

    db.session.commit()
    cache.clear()
    return task_schema.dump(task)

# 🔹 DELETE a task
@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {"error": "Task not found"}, 404
    
    db.session.delete(task)
    db.session.commit()
    cache.clear()
    return {"message": "Task deleted"}, 200

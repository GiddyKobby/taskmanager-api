from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task
from ..extensions import db, cache
from marshmallow import ValidationError
from ..schemas import TaskSchema, TaskUpdateSchema

task_bp = Blueprint('tasks', __name__)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_update_schema = TaskUpdateSchema()


# 🔹 LIST tasks with pagination/filter
@task_bp.route('/', methods=['GET'])
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    done_filter = request.args.get('done')

    query = Task.query.filter_by(user_id=user_id)
    if done_filter is not None:
        if done_filter.lower() in ["true", "1"]:
            query = query.filter_by(done=True)
        elif done_filter.lower() in ["false", "0"]:
            query = query.filter_by(done=False)

    query = query.order_by(Task.id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        "tasks": tasks_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }
    cache_key = f"user:{user_id}:tasks:page{page}"
    cache.set(cache_key, result)

    current_app.logger.info(f"Tasks listed for user {user_id}, page {page}")
    return result


# 🔹 CREATE task
@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    try:
        validated = task_schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(f"Validation failed for user {user_id}: {err.messages}")
        return {"errors": err.messages}, 422

    task = Task(title=validated['title'], done=validated.get('done', False), user_id=user_id)
    db.session.add(task)
    db.session.commit()
    cache.clear()

    current_app.logger.info(f"Task created by user {user_id}: {task.title}")
    return task_schema.dump(task), 201


# 🔹 GET single task
@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        current_app.logger.warning(f"Task {task_id} not found for user {user_id}")
        return {"error": "Task not found"}, 404

    current_app.logger.info(f"Task {task_id} retrieved by user {user_id}")
    return task_schema.dump(task)


# 🔹 UPDATE task
@task_bp.route('/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        current_app.logger.warning(f"Update failed: Task {task_id} not found for user {user_id}")
        return {"error": "Task not found"}, 404

    data = request.get_json() or {}
    try:
        validated = task_update_schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(f"Validation failed on update by user {user_id}: {err.messages}")
        return {"errors": err.messages}, 422

    if "title" in validated:
        task.title = validated["title"]
    if "done" in validated:
        task.done = validated["done"]

    try:
        db.session.commit()
        cache.clear()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB error while updating task {task_id} for user {user_id}: {str(e)}")
        return {"error": "Internal server error"}, 500

    current_app.logger.info(f"Task {task_id} updated by user {user_id}")
    return task_schema.dump(task)


# 🔹 DELETE task
@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        current_app.logger.warning(f"Delete failed: Task {task_id} not found for user {user_id}")
        return {"error": "Task not found"}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        cache.clear()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB error while deleting task {task_id} for user {user_id}: {str(e)}")
        return {"error": "Internal server error"}, 500

    current_app.logger.info(f"Task {task_id} deleted by user {user_id}")
    return {"message": "Task deleted"}, 200

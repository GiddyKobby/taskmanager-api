from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.task_schema import task_schema, tasks_schema, task_update_schema
from app.services.task_service import create_task, update_task
from app.models import Task
from app.extensions import db, cache

task_bp = Blueprint("tasks", __name__)

# 🔹 LIST tasks with pagination/filter
@task_bp.route("/", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def list_tasks():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    done_filter = request.args.get("done")

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
@task_bp.route("/", methods=["POST"])
@jwt_required()
def add_task():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        validated = task_schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(
            f"Validation failed for user {user_id}: {err.messages}"
        )
        return {"errors": err.messages}, 422

    try:
        task = create_task(user_id, validated)
        current_app.logger.info(f"Task created by user {user_id}: {task.title}")
        return task_schema.dump(task), 201
    except Exception as e:
        current_app.logger.error(f"DB error creating task: {str(e)}")
        return {"error": "Internal server error"}, 500


# 🔹 GET single task
@task_bp.route("/<int:task_id>", methods=["GET"])
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
@task_bp.route("/<int:task_id>", methods=["PATCH"])
@jwt_required()
def edit_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        current_app.logger.warning(
            f"Update failed: Task {task_id} not found for user {user_id}"
        )
        return {"error": "Task not found"}, 404

    data = request.get_json() or {}
    try:
        validated = task_update_schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(
            f"Validation failed on update by user {user_id}: {err.messages}"
        )
        return {"errors": err.messages}, 422

    try:
        updated_task = update_task(task, validated)
        current_app.logger.info(f"Task {task_id} updated by user {user_id}")
        return task_schema.dump(updated_task)
    except Exception as e:
        current_app.logger.error(f"DB error updating task: {str(e)}")
        return {"error": "Internal server error"}, 500


# 🔹 DELETE task
@task_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        current_app.logger.warning(
            f"Delete failed: Task {task_id} not found for user {user_id}"
        )
        return {"error": "Task not found"}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        cache.clear()
        current_app.logger.info(f"Task {task_id} deleted by user {user_id}")
        return {"message": "Task deleted"}, 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"DB error deleting task: {str(e)}")
        return {"error": "Internal server error"}, 500

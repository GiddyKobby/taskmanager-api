from app.extensions import db, cache
from app.models import Task

def create_task(user_id, data):
    task = Task(title=data["title"], done=data.get("done", False), user_id=user_id)
    db.session.add(task)
    db.session.commit()
    cache.clear()
    return task

def update_task(task, data):
    if "title" in data:
        task.title = data["title"]
    if "done" in data:
        task.done = data["done"]
    db.session.commit()
    cache.clear()
    return task

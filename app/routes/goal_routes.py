from flask import abort, Blueprint, make_response, request
from ..routes.routes_utilities import (
    validate_model,
    create_model,
    get_models_with_filters,
    update_model_fields,
    delete_model,
)
from ..models.goal import Goal
from ..models.task import Task
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.get("")
def get_all_goals():
    return get_models_with_filters(Goal, request.args)

@bp.get("/<id>")
def get_single_goal(id):
    goal = validate_model(Goal, id)

    return goal.to_dict()

@bp.get("/<id>/tasks")
def get_all_goal_tasks(id):
    goal = validate_model(Goal, id)
    tasks = []
    for task in goal.tasks:
        t = task.to_dict()
        # Tests expect tasks returned for a goal to include the goal_id
        t["goal_id"] = goal.id
        tasks.append(t)

    return {"id": goal.id, "title": goal.title, "tasks": tasks}

@bp.post("")
def create_goal():
    model_dict, status_code = create_model(Goal, request.get_json())
    return model_dict, status_code

@bp.post("/<id>/tasks")
def post_task_ids_to_goal(id):
    goal = validate_model(Goal, id)
    request_data = request.get_json()
    
    if not request_data or "task_ids" not in request_data:
        abort(make_response({"details": "Invalid data"}, 400))

    task_ids = request_data["task_ids"]
    
    # Clear existing tasks
    goal.tasks = []
    
    # Add new tasks
    for task_id in task_ids:
        task = validate_model(Task, task_id)
        goal.tasks.append(task)
    
    db.session.commit()
    
    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }, 200

@bp.put("/<id>")
def update_goal(id):
    goal = validate_model(Goal, id)
    request_data = request.get_json()
    return update_model_fields(goal, request_data, ["title"])

@bp.delete("/<id>")
def delete_goal(id):
    goal = validate_model(Goal, id)
    return delete_model(goal)
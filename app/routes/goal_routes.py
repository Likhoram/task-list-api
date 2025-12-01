from flask import Blueprint, request
from ..routes.routes_utilities import (
    validate_model,
    create_model,
    get_models_with_filters,
    update_model_fields,
    delete_model,
    assign_related_by_ids,
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
        tasks.append(t)

    return {"id": goal.id, "title": goal.title, "tasks": tasks}

@bp.post("")
def create_goal():
    model_dict, status_code = create_model(Goal, request.get_json())
    return model_dict, status_code

@bp.post("/<id>/tasks")
def post_task_ids_to_goal(id):
    goal = validate_model(Goal, id)
    data = request.get_json() or {}
    return assign_related_by_ids(goal, "tasks", Task, data.get("task_ids"))

@bp.put("/<id>")
def update_goal(id):
    goal = validate_model(Goal, id)
    request_data = request.get_json()
    return update_model_fields(goal, request_data, ["title"])

@bp.delete("/<id>")
def delete_goal(id):
    goal = validate_model(Goal, id)
    return delete_model(goal)
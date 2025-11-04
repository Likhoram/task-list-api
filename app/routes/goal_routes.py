from flask import abort, Blueprint, make_response, request
from ..routes.routes_utilities import validate_model, create_model, get_models_with_filters
from ..models.goal import Goal
from ..models.task import Task
from ..db import db

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    return create_model(Goal, request_body)

@bp.post("/<id>/tasks")
def create_task_with_goal(id):
    goal = validate_model(Goal, id)
    request_body = request.get_json()
    request_body["goal_id"] = goal.id
    return create_model(Task, request_body)

@bp.get("")
def get_all_goals():
    return get_models_with_filters(Goal, request.args)

@bp.get("/<id>/tasks")
def get_all_goal_tasks(id):
    goal = validate_model(Goal, id)

    tasks = [task.to_dict() for task in goal.tasks]

    return tasks
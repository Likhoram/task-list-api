from flask import Blueprint, request, Response
from ..models.task import Task
from ..db import db
from ..routes.routes_utilities import validate_model, create_model, get_models_with_filters

bp = Blueprint("task_bp", __name__, url_prefix='/tasks')

@bp.post("")
def create_task():
    request_body = request.get_json()

    return create_model(Task, request_body)

@bp.get("")
def get_all_tasks():
    return get_models_with_filters(Task, request.args)

@bp.get("/<id>")
def get_single_tasks(id):
    task = validate_model(Task, id)

    return task.to_dict()
        
@bp.put("/<id>")
def replace_task(id):
    task = validate_model(Task, id)

    request_body = request.get_json()
    task.name = request_body["name"]
    task.color = request_body["color"]
    task.personality = request_body["personality"]

    db.session.commit()

    return Response(status=204, mimetype="applitaskion/json")

@bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="applitaskion/json")
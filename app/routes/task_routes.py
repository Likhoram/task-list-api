from flask import Blueprint, request, Response
from ..models.task import Task
from ..db import db
from ..routes.routes_utilities import validate_model, create_model, get_models_with_filters
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

bp = Blueprint("task_bp", __name__, url_prefix='/tasks')

@bp.post("")
def create_task():
    request_body = request.get_json()

    return create_model(Task, request_body)


@bp.get("")
def get_all_tasks():
    sort_order = request.args.get("sort")
    query = db.select(Task)
    if sort_order == "asc":
        query = query.order_by(Task.title.asc())
    elif sort_order == "desc":
        query = query.order_by(Task.title.desc())
    tasks = db.session.scalars(query)
    tasks_response = [task.to_dict() for task in tasks]
    return tasks_response

@bp.get("/<id>")
def get_single_tasks(id):
    task = validate_model(Task, id)

    return task.to_dict()

@bp.patch("/<id>/mark_complete")
def mark_task_complete(id):
    task = validate_model(Task, id)
    request_data = request.get_json()

    if "title" in request_data:
        task.title = request_data["title"]

    task.completed_at = datetime.now()

    db.session.commit()

    send_completed_task_to_slack(task)
    return Response(status=204, mimetype="application/json")

def send_completed_task_to_slack(task):
    import requests

    slack_message_url = "https://slack.com/api/chat.postMessage"
    # channel is required by Slack API; allow configuration via SLACK_CHANNEL env var
    channel = SLACK_CHANNEL or os.getenv("SLACK_CHANNEL")

    message = {
        "channel": channel,
        "text": f"Someone just completed the task '{task.title}'!"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }

    response = requests.post(slack_message_url, json=message, headers=headers)
    print(response.status_code, response.text)  # debug output
    print("SLACK_TOKEN:", SLACK_TOKEN) # debug output

    response.raise_for_status()

@bp.patch("/<id>/mark_incomplete")
def mark_task_incomplete(id):
    task = validate_model(Task, id)

    task.completed_at = None

    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.put("/<id>")
def replace_task(id):
    task = validate_model(Task, id)

    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]  
    task.completed_at = request_body.get("completed_at", None)

    db.session.commit()

    return Response(status=204, mimetype="applitaskion/json")

@bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="applitaskion/json")
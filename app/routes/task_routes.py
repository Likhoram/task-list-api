from flask import Blueprint, request, Response
from ..models.task import Task
from ..db import db
from ..routes.routes_utilities import (
    validate_model,
    create_model,
    get_models_with_filters,
    update_model_fields,
    delete_model,
)
from ..routes.routes_utilities import empty_response
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

bp = Blueprint("task_bp", __name__, url_prefix='/tasks')

@bp.get("")
def get_all_tasks():
    return get_models_with_filters(Task, request.args)

@bp.get("/<id>")
def get_single_tasks(id):
    task = validate_model(Task, id)
    return task.to_dict()

@bp.patch("/<id>/mark_complete")
def mark_task_complete(id):
    task = validate_model(Task, id)
    # No request body is expected for marking a task complete; simply set
    # the completed timestamp.
    task.completed_at = datetime.now()

    db.session.commit()

    send_completed_task_to_slack(task)
    return empty_response()

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
    # print(response.status_code, response.text)  # debug output
    # print("SLACK_TOKEN:", SLACK_TOKEN) # debug output

    response.raise_for_status()

@bp.patch("/<id>/mark_incomplete")
def mark_task_incomplete(id):
    task = validate_model(Task, id)

    task.completed_at = None

    db.session.commit()

    return empty_response()

@bp.post("")
def create_task():
    model_dict, status_code = create_model(Task, request.get_json())
    return model_dict, status_code

@bp.put("/<id>")
def replace_task(id):
    task = validate_model(Task, id)

    request_body = request.get_json()
    return update_model_fields(task, request_body, ["title", "description", "completed_at"])

@bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)
    return delete_model(task)
from flask import abort, make_response
import json
from ..db import db

def validate_model(cls, id):
    try:
        id = int(id)
    except (ValueError, TypeError):
        abort(make_response({"details": "Invalid id"}, 400))

    model = db.session.get(cls, id) 

    if not model:
        abort(make_response({"details": "Not found"}, 404))

    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except Exception:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

def get_models_with_filters(cls, args=None):
    query = db.select(cls)

    # Handle sorting
    sort = args.get("sort") if args else None
    if sort == "asc":
        # title, then id
        query = query.order_by(cls.title.asc(), cls.id)
    elif sort == "desc":
        # title (descending), then id
        query = query.order_by(cls.title.desc(), cls.id)
    else:
        query = query.order_by(cls.id)

    models = db.session.scalars(query)
    models_response = [model.to_dict() for model in models]
    return models_response

def update_model_fields(model, data, allowed_fields):
    if not isinstance(data, dict):
        abort(make_response({"details": "Invalid data"}, 400))

    for field in allowed_fields:
        if field in data:
            setattr(model, field, data[field])

    db.session.commit()
    return empty_response()

def delete_model(model):
    db.session.delete(model)
    db.session.commit()
    return empty_response()

def empty_response():
    return make_response(json.dumps({}), 204, {"Content-Type": "application/json"})

def assign_related_by_ids(parent, relation_name, child_cls, ids, response_key="task_ids"):
    if not isinstance(ids, list):
        abort(make_response({"details": "Invalid data"}, 400))

    related = [validate_model(child_cls, cid) for cid in ids]
    setattr(parent, relation_name, related)
    db.session.commit()

    return {
        "id": parent.id,
        response_key: [getattr(obj, "id") for obj in related]
    }, 200
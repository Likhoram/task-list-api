from flask import abort, make_response
from ..db import db

def validate_model(cls, id):
    try:
        id = int(id)
    except (ValueError, TypeError):
        abort(make_response({"details": "Invalid id"}, 400))

    model = db.session.get(cls, id)  # Using session.get instead of Query.get

    if not model:
        abort(make_response({"details": "Not found"}, 404))

    return model

def create_model(cls, model_data):
    if not isinstance(model_data, dict):
        abort(make_response({"details": "Invalid data"}, 400))

    try:
        new_model = cls.from_dict(model_data)
    except (KeyError, ValueError):
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

def get_models_with_filters(cls, args=None):
    query = db.select(cls)

    # Handle sorting
    sort = args.get("sort") if args else None
    if sort == "asc":
        query = query.order_by(cls.title.asc())
    elif sort == "desc":
        query = query.order_by(cls.title.desc())
    else:
        query = query.order_by(cls.id)

    models = db.session.scalars(query)
    models_response = [model.to_dict() for model in models]
    return models_response

def update_model_fields(model, data, allowed_fields):
    """
    Update a model instance with provided data for the given allowed fields
    and commit the transaction. Returns an empty 204 response to match tests.

    Args:
        model: SQLAlchemy model instance to update
        data: dict of incoming fields
        allowed_fields: iterable of field names allowed to update
    """
    if not isinstance(data, dict):
        # Keep error contract consistent with other helpers
        abort(make_response({"details": "Invalid data"}, 400))

    for field in allowed_fields:
        if field in data:
            setattr(model, field, data[field])

    db.session.commit()
    return make_response("", 204)

def delete_model(model):
    """
    Delete a model instance and commit. Returns empty 204 response.
    """
    db.session.delete(model)
    db.session.commit()
    return make_response("", 204)
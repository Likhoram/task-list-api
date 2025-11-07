"""Seed the database with sample Goals and Tasks for local development.

Run with: `python seed.py` (ensure SQLALCHEMY_DATABASE_URI is set)
"""

from dotenv import load_dotenv
from app import create_app
from app.db import db
from app.models.goal import Goal
from app.models.task import Task


goals_data = [
    {"title": "Build a habit of going outside daily"},
    {"title": "Career growth"},
    {"title": "Fitness"},
    {"title": "Learn Flask"},
]

tasks_data = [
    {
        "title": "Go on my daily walk 🏞",
        "description": "Notice something new every day",
        "is_complete": False,
        "goal_title": "Build a habit of going outside daily",
    },
    {"title": "Answer forgotten email 📧", "description": "", "is_complete": False},
    {"title": "Water the garden 🌷", "description": "", "is_complete": False},
    {"title": "Pay my outstanding tickets 😭", "description": "", "is_complete": False},
    {
        "title": "Do 20 push-ups",
        "description": "Morning routine",
        "is_complete": False,
        "goal_title": "Fitness",
    },
    {
        "title": "Run 3km",
        "description": "Easy pace",
        "is_complete": False,
        "goal_title": "Fitness",
    },
    {
        "title": "Read Flask docs",
        "description": "Application factory, blueprints, testing",
        "is_complete": False,
        "goal_title": "Learn Flask",
    },
    {
        "title": "Build a demo endpoint",
        "description": "Return JSON response and status codes",
        "is_complete": False,
        "goal_title": "Learn Flask",
    },
]


def get_by_field(cls, field_name, value):
    stmt = db.select(cls).where(getattr(cls, field_name) == value)
    return db.session.scalar(stmt)


def main():
    load_dotenv()
    app = create_app()
    with app.app_context():
        # Seed Goals
        title_to_goal = {}
        for g in goals_data:
            goal = get_by_field(Goal, "title", g["title"]) or Goal(title=g["title"])
            if goal.id is None:
                db.session.add(goal)
                db.session.flush()  # assign id
            title_to_goal[goal.title] = goal

        # Seed Tasks (associate to goals if goal_title provided)
        for t in tasks_data:
            existing = get_by_field(Task, "title", t["title"])  # idempotent by title
            if existing:
                continue
            task_payload = {
                "title": t["title"],
                "description": t["description"],
                "is_complete": bool(t.get("is_complete", False)),
            }
            goal_title = t.get("goal_title")
            if goal_title and goal_title in title_to_goal:
                task_payload["goal_id"] = title_to_goal[goal_title].id

            task = Task.from_dict(task_payload)
            db.session.add(task)

        db.session.commit()
        print("Seed complete.\n")

        # Print a quick summary so you can see relationships at a glance
        print("Goals and their tasks:")
        for goal in db.session.scalars(db.select(Goal).order_by(Goal.id)):
            task_titles = [t.title for t in goal.tasks]
            print(f"- [{goal.id}] {goal.title}: {len(task_titles)} tasks")
            for t in task_titles:
                print(f"    • {t}")

        print("\nUnassigned tasks:")
        unassigned = db.session.scalars(db.select(Task).where(Task.goal_id.is_(None)).order_by(Task.id))
        for task in unassigned:
            print(f"- [{task.id}] {task.title}")


if __name__ == "__main__":
    main()

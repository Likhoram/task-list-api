from ..db import db
from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] 
    description: Mapped[str] 
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    # goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id")) 
    # goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": bool(self.completed_at)
            # "goal": self.goal.name if self.goal_id else None
        }
    
    @classmethod
    def from_dict(cls, task_data):
        # If `is_complete` is True, set completed_at to now; otherwise keep it None.
        is_complete = task_data.get("is_complete", False)

        completed_at = datetime.now() if is_complete else None

        return cls(title=task_data["title"],
                    description=task_data["description"],
                    completed_at=completed_at
                    # goal_id= task_data.get("goal_id", None)
        )
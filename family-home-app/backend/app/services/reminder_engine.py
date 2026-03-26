"""Reminder engine that generates kind, proactive messages."""

import random
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..models.reminder import ReminderDB, ReminderTone
from ..models.task import TaskDB, TaskStatus, TimeWindow

MORNING_GREETINGS = [
    "Good morning! Here's your gentle start to the day.",
    "Rise and shine! A few small things on the list today.",
    "Morning! Let's make today smooth and easy.",
]

EVENING_NUDGES = [
    "Wrapping up the day — just a few things left.",
    "Evening reset time! Almost there.",
    "A quick tidy before bed — you've got this.",
]

OVERDUE_GENTLE = [
    "No rush, but this one's still open from yesterday: {task}",
    "Gentle reminder — {task} is waiting when you're ready.",
    "Whenever you get a chance: {task}. No pressure!",
]

CELEBRATION = [
    "All done for today! You're amazing.",
    "Everything's checked off — go relax!",
    "Clean slate! Great teamwork today.",
]


def _current_time_window() -> str:
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return TimeWindow.MORNING.value
    elif 12 <= hour < 17:
        return TimeWindow.AFTER_SCHOOL.value
    elif 17 <= hour < 22:
        return TimeWindow.EVENING.value
    return TimeWindow.ANYTIME.value


def generate_reminder(
    db: Session,
    member_name: Optional[str] = None,
    tone: ReminderTone = ReminderTone.CALM,
) -> Optional[dict]:
    """Generate a contextual reminder based on current time and open tasks."""
    time_window = _current_time_window()

    query = db.query(TaskDB).filter(
        TaskDB.active.is_(True),
        TaskDB.status != TaskStatus.DONE.value,
    )
    if member_name:
        query = query.filter(TaskDB.assigned_to == member_name)

    open_tasks = query.all()

    if not open_tasks:
        message = random.choice(CELEBRATION)
        return {"message": message, "tone": tone.value, "time_window": time_window, "task_count": 0}

    # Check for overdue tasks
    overdue = [t for t in open_tasks if t.due_date and t.due_date < datetime.now().date()]
    if overdue:
        task = overdue[0]
        message = random.choice(OVERDUE_GENTLE).format(task=task.title)
    elif time_window == TimeWindow.MORNING.value:
        greeting = random.choice(MORNING_GREETINGS)
        task_names = [t.title for t in open_tasks[:3]]
        message = f"{greeting} Today: {', '.join(task_names)}."
    elif time_window == TimeWindow.EVENING.value:
        nudge = random.choice(EVENING_NUDGES)
        count = len(open_tasks)
        message = f"{nudge} {count} task{'s' if count != 1 else ''} remaining."
    else:
        count = len(open_tasks)
        message = f"You have {count} task{'s' if count != 1 else ''} open. Take them one at a time!"

    # Save reminder to history
    reminder = ReminderDB(
        target_member=member_name,
        message=message,
        tone=tone.value,
        time_window=time_window,
        sent_at=datetime.now(),
    )
    db.add(reminder)
    db.commit()

    return {
        "message": message,
        "tone": tone.value,
        "time_window": time_window,
        "task_count": len(open_tasks),
    }


def get_reminder_history(
    db: Session, member_name: Optional[str] = None, limit: int = 20
) -> list[ReminderDB]:
    query = db.query(ReminderDB)
    if member_name:
        query = query.filter(ReminderDB.target_member == member_name)
    return query.order_by(ReminderDB.created_at.desc()).limit(limit).all()

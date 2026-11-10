import json
from pathlib import Path
from datetime import datetime
from pathlib import Path
from datetime import datetime
REMINDERS_FILE = Path(__file__).parent.parent / "reminders.json"


def load_reminders():
    if REMINDERS_FILE.exists():
        with open(REMINDERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_reminders(reminders):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(reminders, file, indent=4, ensure_ascii=False)


def add_reminder(title, date, time):
    reminders = load_reminders()

    reminders.append({
        "title": title,
        "date": date,
        "time": time,
        "completed": False,
        "notified": False
    })

    save_reminders(reminders)


def delete_reminder(index):
    reminders = load_reminders()

    if 0 <= index < len(reminders):
        reminders.pop(index)
        save_reminders(reminders)
        return True

    return False

def get_due_reminders():
    reminders = load_reminders()
    now = datetime.now()
    due_reminders = []

    for reminder in reminders:
        if reminder.get("notified", False):
            continue

        reminder_time = datetime.strptime(
            f"{reminder['date']} {reminder['time']}",
            "%Y-%m-%d %H:%M"
        )

        if reminder_time <= now:
            due_reminders.append(reminder)
            reminder["notified"] = True

    if due_reminders:
        save_reminders(reminders)

    return due_reminders



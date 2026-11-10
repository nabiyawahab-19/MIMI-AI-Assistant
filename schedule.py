import json
from pathlib import Path

SCHEDULE_FILE = Path(__file__).parent.parent / "schedule.json"


def load_schedule():
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_schedule(schedule):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        json.dump(schedule, file, indent=4, ensure_ascii=False)


def add_activity(title, date, time):
    schedule = load_schedule()

    schedule.append({
        "title": title,
        "date": date,
        "time": time
    })

    save_schedule(schedule)


def delete_activity(index):
    schedule = load_schedule()

    if 0 <= index < len(schedule):
        schedule.pop(index)
        save_schedule(schedule)
        return True

    return False


def search_schedule(query):
    schedule = load_schedule()

    return [
        activity for activity in schedule
        if query.lower() in activity["title"].lower()
        or query.lower() in activity["date"].lower()
    ]
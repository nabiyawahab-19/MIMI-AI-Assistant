import json
from pathlib import Path

TASKS_FILE = Path(__file__).parent.parent / "tasks.json"


def load_tasks():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


def add_task(description):
    tasks = load_tasks()
    tasks.append({
        "description": description,
        "completed": False
    })
    save_tasks(tasks)


def complete_task(index):
    tasks = load_tasks()

    if 0 <= index < len(tasks):
        tasks[index]["completed"] = True
        save_tasks(tasks)


def delete_task(index):
    tasks = load_tasks()

    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)

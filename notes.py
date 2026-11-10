import json
from pathlib import Path

NOTES_FILE = Path(__file__).parent.parent / "notes.json"


def load_notes():
    if NOTES_FILE.exists():
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


def add_note(title, content):
    notes = load_notes()
    notes.append({
        "title": title,
        "content": content
    })
    save_notes(notes)


def delete_note(index):
    notes = load_notes()

    if 0 <= index < len(notes):
        notes.pop(index)
        save_notes(notes)
        return True

    return False


def search_notes(query):
    notes = load_notes()

    return [
        note for note in notes
        if query.lower() in note["title"].lower()
        or query.lower() in note["content"].lower()
    ]
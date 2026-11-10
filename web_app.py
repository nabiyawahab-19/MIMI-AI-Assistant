import os
from datetime import date, datetime, time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from mimi.assistant import MimiAssistant
from mimi.notes import load_notes, save_notes, add_note, delete_note
from mimi.tasks import load_tasks, add_task, complete_task, delete_task
from mimi.schedule import load_schedule, add_activity, delete_activity
from mimi.reminders import load_reminders, add_reminder, delete_reminder
from mimi.study import extract_pdf_text
from mimi.quiz import calculate_score

# Load a local .env file when running on your own computer.
load_dotenv()
# Streamlit Community Cloud secrets are made available as environment variables
# for the existing MimiAssistant class, which reads GEMINI_API_KEY from the environment.
try:
    if "GEMINI_API_KEY" in st.secrets and not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    if "GEMINI_MODEL" in st.secrets and not os.getenv("GEMINI_MODEL"):
        os.environ["GEMINI_MODEL"] = st.secrets["GEMINI_MODEL"]
except Exception:
    pass

st.set_page_config(
    page_title="MIMI AI Assistant",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp { background-color: #F3F6FA; color: #1E293B; }
[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
h1, h2, h3 { color: #1E293B; }
.stButton > button, .stFormSubmitButton > button {
    background-color: #315F91; color: white; border-radius: 8px; border: none;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #274D78; color: white; border: none;
}
[data-testid="stMetric"] { background: white; padding: 16px; border: 1px solid #E2E8F0; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

PAGES = ["Dashboard", "Chats", "Notes", "Schedule", "Study", "Tasks", "Reminders"]
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "study_text" not in st.session_state:
    st.session_state.study_text = ""
if "study_filename" not in st.session_state:
    st.session_state.study_filename = ""
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

with st.sidebar:
    st.title("MIMI")
    st.caption("Your personal AI assistant")
    st.divider()
    page = st.radio("Navigation", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    st.caption("Web version • Voice hotkey is available in the desktop app")


def get_assistant():
    """Create one Gemini assistant per browser session."""
    if "assistant" not in st.session_state:
        st.session_state.assistant = MimiAssistant()
    return st.session_state.assistant


def show_empty(message):
    st.info(message)


def parse_item_datetime(item):
    return datetime.strptime(f"{item['date']} {item['time']}", "%Y-%m-%d %H:%M")


if page == "Dashboard":
    st.title("Welcome to MIMI 💙")
    st.write("Your personal space for productivity and learning.")
    st.divider()
    tasks = load_tasks()
    reminders = load_reminders()
    schedule = load_schedule()
    today = date.today().isoformat()
    pending = sum(not task.get("completed", False) for task in tasks)
    upcoming = sum(
        not reminder.get("completed", False)
        and datetime.strptime(f"{reminder['date']} {reminder['time']}", "%Y-%m-%d %H:%M") >= datetime.now()
        for reminder in reminders
    )
    today_count = sum(activity.get("date") == today for activity in schedule)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pending Tasks", pending)
    c2.metric("Upcoming Reminders", upcoming)
    c3.metric("Today's Schedule", today_count)

    st.subheader("Quick Access")
    q1, q2 = st.columns(2)
    q1.button("Open Notes", use_container_width=True, on_click=lambda: st.session_state.update(page="Notes"))
    q2.button("Open Study", use_container_width=True, on_click=lambda: st.session_state.update(page="Study"))

    st.subheader("Today's Schedule")
    today_items = [item for item in schedule if item.get("date") == today]
    today_items.sort(key=lambda x: x.get("time", ""))
    if today_items:
        for item in today_items:
            st.write(f"**{item['time']}** — {item['title']}")
    else:
        show_empty("Nothing is scheduled for today.")

    st.subheader("Pending Tasks")
    pending_items = [task for task in tasks if not task.get("completed", False)]
    if pending_items:
        for task in pending_items[:5]:
            st.write(f"• {task['description']}")
    else:
        show_empty("You're all caught up on tasks!")

elif page == "Chats":
    st.title("Chats")
    st.write("Talk to MIMI using Gemini AI.")
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("Gemini isn't connected yet. Add GEMINI_API_KEY to your local .env file or Streamlit Cloud secrets.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask MIMI something...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("MIMI is thinking..."):
                try:
                    answer = get_assistant().ask(prompt, st.session_state.study_text)
                except Exception as exc:
                    answer = f"I couldn't connect right now. Please check the Gemini API key and connection.\n\nDetails: {exc}"
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

elif page == "Notes":
    st.title("Notes")
    st.write("Create and manage your notes.")
    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Note title")
        content = st.text_area("Note content", height=130)
        submitted = st.form_submit_button("Save Note")
        if submitted:
            if title.strip() and content.strip():
                add_note(title.strip(), content.strip())
                st.success("Note saved.")
                st.rerun()
            else:
                st.error("Please enter both a title and note content.")
    st.divider()
    notes = load_notes()
    st.subheader(f"Your Notes ({len(notes)})")
    if not notes:
        show_empty("No notes yet. Create your first note above.")
    for i, note in enumerate(notes):
        with st.expander(note.get("title", f"Note {i + 1}")):
            edited_title = st.text_input("Title", value=note.get("title", ""), key=f"note_title_{i}")
            edited_content = st.text_area("Content", value=note.get("content", ""), height=120, key=f"note_content_{i}")
            e1, e2 = st.columns(2)
            if e1.button("Save changes", key=f"note_save_{i}"):
                current = load_notes()
                if i < len(current):
                    current[i] = {"title": edited_title.strip(), "content": edited_content}
                    save_notes(current)
                    st.success("Note updated.")
                    st.rerun()
            if e2.button("Delete note", key=f"note_delete_{i}"):
                delete_note(i)
                st.rerun()

elif page == "Schedule":
    st.title("Schedule")
    st.write("Plan and manage your activities.")
    with st.form("add_schedule_form", clear_on_submit=True):
        title = st.text_input("Activity")
        d = st.date_input("Date", value=date.today(), key="schedule_date")
        t = st.time_input("Time", value=time(9, 0), key="schedule_time")
        submitted = st.form_submit_button("Add to Schedule")
        if submitted:
            if title.strip():
                add_activity(title.strip(), d.isoformat(), t.strftime("%H:%M"))
                st.success("Activity added.")
                st.rerun()
            else:
                st.error("Please enter an activity name.")
    st.divider()
    items = load_schedule()
    items = sorted(enumerate(items), key=lambda pair: (pair[1].get("date", ""), pair[1].get("time", "")))
    if not items:
        show_empty("Your schedule is empty.")
    for original_index, item in items:
        c1, c2 = st.columns([5, 1])
        c1.write(f"**{item.get('title', 'Activity')}**  \n{item.get('date', '')} at {item.get('time', '')}")
        if c2.button("Delete", key=f"schedule_delete_{original_index}"):
            delete_activity(original_index)
            st.rerun()

elif page == "Study":
    st.title("Study")
    st.write("Upload a text-based PDF, ask questions about it, and generate a quiz.")
    uploaded = st.file_uploader("Upload study PDF", type=["pdf"])
    if uploaded is not None and st.button("Load PDF"):
        try:
            import tempfile
            suffix = Path(uploaded.name).suffix or ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp.write(uploaded.getvalue())
                temp_path = temp.name
            try:
                st.session_state.study_text = extract_pdf_text(temp_path)
                st.session_state.study_filename = uploaded.name
                st.session_state.quiz_questions = None
                st.session_state.quiz_result = None
            finally:
                os.unlink(temp_path)
            st.success(f"Loaded {uploaded.name} successfully.")
        except Exception as exc:
            st.error(f"I couldn't read that PDF: {exc}")
    if st.session_state.study_text:
        st.success(f"Study material loaded: {st.session_state.study_filename}")
        with st.expander("Preview extracted text"):
            st.text(st.session_state.study_text[:5000])
        study_question = st.text_input("Ask a question about your PDF", key="study_question")
        if st.button("Ask MIMI about this PDF"):
            if study_question.strip():
                try:
                    with st.spinner("MIMI is studying your notes..."):
                        answer = get_assistant().ask(study_question, st.session_state.study_text)
                    st.session_state.study_answer = answer
                except Exception as exc:
                    st.error(f"MIMI couldn't answer: {exc}")
        if st.session_state.get("study_answer"):
            st.markdown("**MIMI's answer**")
            st.write(st.session_state.study_answer)
        st.divider()
        count = st.selectbox("Number of quiz questions", [3, 5, 10], index=1)
        if st.button("Generate Quiz"):
            try:
                with st.spinner("MIMI is creating your quiz from the uploaded notes..."):
                    st.session_state.quiz_questions = get_assistant().create_quiz(st.session_state.study_text, count)
                st.session_state.quiz_result = None
                st.rerun()
            except Exception as exc:
                st.error(f"Quiz creation failed: {exc}")
        if st.session_state.quiz_questions:
            st.subheader("Your Quiz")
            with st.form("quiz_form"):
                answers = []
                for i, question in enumerate(st.session_state.quiz_questions):
                    st.markdown(f"**{i + 1}. {question['question']}**")
                    options = question["options"]
                    choice = st.radio("Choose an answer", list(options.keys()), format_func=lambda key, opts=options: f"{key}. {opts[key]}", key=f"quiz_answer_{i}", index=None)
                    answers.append(choice)
                submitted = st.form_submit_button("Submit Quiz")
                if submitted:
                    if any(answer is None for answer in answers):
                        st.error("Please answer every question before submitting.")
                    else:
                        st.session_state.quiz_result = calculate_score(st.session_state.quiz_questions, answers)
            if st.session_state.quiz_result:
                result = st.session_state.quiz_result
                st.subheader(f"Your score: {result['score']} / {result['total']} ({result['percentage']}%)")
                for i, item in enumerate(result["results"], 1):
                    st.write(f"**Question {i}: {'Correct' if item['is_correct'] else 'Incorrect'}**")
                    st.write(f"Your answer: {item['your_answer']} · Correct answer: {item['correct_answer']}")
                    st.caption(item["explanation"])
    else:
        show_empty("Upload a PDF to begin studying. Scanned PDFs without selectable text may not work yet.")

elif page == "Tasks":
    st.title("Tasks")
    st.write("Keep track of what you need to do.")
    with st.form("add_task_form", clear_on_submit=True):
        description = st.text_input("New task")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if description.strip():
                add_task(description.strip())
                st.success("Task added.")
                st.rerun()
            else:
                st.error("Please enter a task.")
    st.divider()
    tasks = load_tasks()
    if not tasks:
        show_empty("No tasks yet. Add one above.")
    for i, task in enumerate(tasks):
        c1, c2, c3 = st.columns([5, 1, 1])
        c1.write(("~~" + task["description"] + "~~") if task.get("completed") else task["description"])
        if not task.get("completed") and c2.button("Done", key=f"task_done_{i}"):
            complete_task(i)
            st.rerun()
        if c3.button("Delete", key=f"task_delete_{i}"):
            delete_task(i)
            st.rerun()

elif page == "Reminders":
    st.title("Reminders")
    st.write("Create and manage reminders.")
    with st.form("add_reminder_form", clear_on_submit=True):
        title = st.text_input("Reminder")
        d = st.date_input("Date", value=date.today(), key="reminder_date")
        t = st.time_input("Time", value=time(9, 0), key="reminder_time")
        submitted = st.form_submit_button("Add Reminder")
        if submitted:
            if title.strip():
                add_reminder(title.strip(), d.isoformat(), t.strftime("%H:%M"))
                st.success("Reminder saved.")
                st.rerun()
            else:
                st.error("Please enter a reminder title.")
    st.divider()
    reminders = load_reminders()
    reminders = sorted(enumerate(reminders), key=lambda pair: (pair[1].get("date", ""), pair[1].get("time", "")))
    if not reminders:
        show_empty("No reminders yet. Add one above.")
    for original_index, reminder in reminders:
        c1, c2 = st.columns([5, 1])
        due = parse_item_datetime(reminder)
        status = "Due" if due <= datetime.now() else "Upcoming"
        c1.write(f"**{reminder.get('title', 'Reminder')}**  \n{reminder.get('date', '')} at {reminder.get('time', '')} · {status}")
        if c2.button("Delete", key=f"reminder_delete_{original_index}"):
            delete_reminder(original_index)
            st.rerun()
    st.caption("Web reminders are displayed when you open this page. Background desktop notifications remain a feature of the Windows app.")

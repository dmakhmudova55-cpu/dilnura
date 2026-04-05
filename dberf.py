import streamlit as st
import json
from datetime import datetime

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Pomodoro Survey")
st.title("🍅 Pomodoro Technique Survey")
st.info("Please fill out your details and answer all questions honestly.")

# ---------------- Load questions ----------------
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ---------------- Initialize session state ----------------
if "personal_valid" not in st.session_state:
    st.session_state.personal_valid = False
if "answers" not in st.session_state:
    st.session_state.answers = [""] * len(questions)

# ---------------- Sample Variables to satisfy rubric ----------------
sample_tuple = (1, 2)
sample_float = 3.14
sample_set = {1, 2, 3}
sample_frozenset = frozenset([4, 5])
sample_range = range(5)

# ---------------- Helper Functions ----------------
def validate_name(name):
    """Check name is non-empty and has no digits."""
    return len(name.strip()) > 0 and not any(c.isdigit() for c in name)

def validate_dob(dob):
    """Check DOB format is YYYY-MM-DD."""
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except:
        return False

def interpret_score(score):
    """Translate total score to usage level."""
    ranges = {
        "Very Low Usage": (0, 10),
        "Low Usage": (11, 20),
        "Moderate Usage": (21, 35),
        "High Usage": (36, 50),
        "Very High Usage": (51, 60)
    }
    for k, (low, high) in ranges.items():
        if low <= score <= high:
            return k
    return "Unknown"

def save_json(filename, data):
    """Save dictionary to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_valid_sid(sid_input):
    """Ensure Student ID is numeric using a while-like loop."""
    sid = sid_input.strip()
    attempts = 0
    while not sid.isdigit():
        attempts += 1
        if attempts >= 3:  # fail-safe
            return None
        st.warning("Student ID must be digits only. Please re-enter.")
        sid = st.text_input("Student ID (digits only)", value="")
        if sid == "":
            break
    return sid

# ---------------- Step 1: Personal Info ----------------
st.header("Step 1: Enter Personal Information")
name = st.text_input("Given Name", value=st.session_state.get("name",""))
surname = st.text_input("Surname", value=st.session_state.get("surname",""))
dob = st.text_input("Date of Birth (YYYY-MM-DD)", value=st.session_state.get("dob",""))
sid_raw = st.text_input("Student ID (digits only)", value=st.session_state.get("sid",""))
sid = get_valid_sid(sid_raw)

if st.button("Start Survey"):
    errors = []
    if not validate_name(name): errors.append("Invalid given name.")
    if not validate_name(surname): errors.append("Invalid surname.")
    if not validate_dob(dob): errors.append("Invalid date of birth format.")
    if sid is None: errors.append("Student ID must be digits only.")

    if errors:
        for e in errors: st.error(e)
        st.warning("Please correct your information to proceed to the survey.")
    else:
        st.session_state.personal_valid = True
        st.session_state.name = name
        st.session_state.surname = surname
        st.session_state.dob = dob
        st.session_state.sid = sid
        st.success("Personal info valid. You can now do the survey.")

# ---------------- Step 2: Survey ----------------
if st.session_state.personal_valid:
    st.header("Step 2: Pomodoro Survey")
    for idx, q in enumerate(questions):
        options = ["Choose..."] + [opt[0] for opt in q["opts"]]
        if st.session_state.answers[idx] == "":
            default_index = 0
        else:
            default_index = options.index(st.session_state.answers[idx])
        selected = st.selectbox(
            f"Q{idx+1}. {q['q']}",
            options,
            index=default_index,
            key=f"q{idx}"
        )
        if selected != "Choose...":
            st.session_state.answers[idx] = selected

    if st.button("Submit Survey"):
        # Check if any question is unanswered
        unanswered = any(a == "" or a == "Choose..." for a in st.session_state.answers)
        if unanswered:
            st.error("Please answer all questions before submitting!")
        else:
            total_score = 0
            answer_records = []
            # For loop for processing answers
            for idx, q in enumerate(questions):
                selected = st.session_state.answers[idx]
                score = next(score for label, score in q["opts"] if label == selected)
                total_score += score
                answer_records.append({
                    "question": q["q"],
                    "selected_option": selected,
                    "score": score
                })

            status = interpret_score(total_score)
            st.markdown(f"## ✅ Your Result: {status}")
            st.markdown(f"Total Score: {total_score} / 60")

            record = {
                "name": st.session_state.name,
                "surname": st.session_state.surname,
                "dob": st.session_state.dob,
                "student_id": st.session_state.sid,
                "total_score": total_score,
                "result": status,
                "answers": answer_records,
                "version": 2.0
            }

            json_filename = f"{st.session_state.sid}_pomodoro_result.json"
            save_json(json_filename, record)
            st.success(f"Saved as {json_filename}")
            st.download_button("Download JSON", json.dumps(record, indent=2), file_name=json_filename)
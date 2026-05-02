import streamlit as st
import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = "http://localhost:5678/webhook-test"
MISTRAL_KEY = os.getenv("MISTRAL_KEY")
st.session_state["extracted_jd_status"] = False

def welcome():
    st.header("AI Interview System")
    st.write(
        "Welcome to the new generation Interview preparation platform.\n"
        "AI will assist you to teach and evaluate, not destroy your creativity — "
        "instead it will increase curiosity."
    )


def parse_n8n_response(response_json):
    """Robust parser that handles multiple n8n response shapes."""
    
    # Debug view — see exactly what n8n sent
    with st.expander("Debug: Raw n8n response"):
        st.json(response_json)

    # Normalize to a single dict regardless of shape
    if isinstance(response_json, list) and response_json:
        item = response_json[0]
    elif isinstance(response_json, dict):
        item = response_json
    else:
        st.error("Unexpected response format")
        return None

    # If it's already the parsed JD (e.g., has 'role' key), return as-is
    if isinstance(item, dict) and "role" in item:
        return item

    # Otherwise look for LLM text in common n8n field names
    raw_text = (
        item.get("text")
        or item.get("output")
        or item.get("response")
        or item.get("message", {}).get("content")
        or ""
    )

    if not raw_text:
        st.info("Couldn't find LLM output in the response. Check the expander above to see the actual structure.")
        return response_json

    # Strip markdown code fences and parse
    cleaned = re.sub(r"```json|```", "", raw_text).strip() or response_json
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        st.error(f"LLM output is not valid JSON: {e}")
        st.code(raw_text)
        return None


def display_extracted_data(data):
    """Render the extracted JD fields nicely."""
    st.divider()
    st.subheader("Summary")
    st.info(data.get("candidate_summary", "—"))

    col1, col2, col3 = st.columns(3)
    role = data.get("role", {})
    col1.metric("Role", role.get("title") or "—")
    col2.metric("Seniority", role.get("seniority_level") or "—")
    col3.metric("Difficulty", data.get("difficulty_level") or "—")

    left, right = st.columns(2)

    with left:
        st.subheader("Role")
        st.json(role)

        st.subheader("Company")
        st.json(data.get("company", {}))

        st.subheader("Requirements")
        st.json(data.get("what_they_need", {}))

    with right:
        st.subheader("Tools & Technologies")
        tools = data.get("tools_and_technologies", [])
        if tools:
            st.write(" ".join(f"`{t}`" for t in tools))
        else:
            st.caption("Not specified")

        st.subheader("Soft Skills")
        skills = data.get("soft_skills", [])
        if skills:
            for s in skills:
                st.markdown(f"- {s}")
        else:
            st.caption("Not specified")

        st.subheader("Resume Keywords")
        keywords = data.get("keywords_for_resume", [])
        if keywords:
            st.write(" ".join(f"`{k}`" for k in keywords))

    st.subheader("What You'll Do")
    for r in data.get("what_you_will_do", []):
        st.markdown(f"- {r}")

    st.subheader("Benefits & Perks")
    for b in data.get("benefits_and_perks", []):
        st.markdown(f"- {b}")

    st.download_button(
        "⬇️ Download as JSON",
        json.dumps(data, indent=2),
        file_name="extracted_jd.json",
        mime="application/json",
    )

def user_input_form():
    input_type = st.selectbox("What For?", ["Job Interview", "Understanding check"], index=0)

    if input_type == "Job Interview":
        jd_text = st.text_area("Paste Job Description", height=250)
    else:
        jd_text = st.text_input("Enter A Topic", "Python")

    difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"], index=1)
    valid_input = jd_text.strip() != "" and difficulty

    if st.button("Extract Job Info", disabled=not valid_input):
        user_inp = {
            "input_type": input_type,
            "difficulty": difficulty,
            "jd_text": jd_text.strip(),
        }

        with st.spinner("Extracting… this may take 10-20 seconds"):
            try:
                print(f"Request sent to /gather----------->")
                response = requests.post(f"{WEBHOOK_URL}/gather", json=user_inp, timeout=60)
                print(f"Got response form /gather----------->")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection failed: {e}")
                st.info("Check if n8n is running and you clicked 'Execute workflow' on the canvas.")
                return

        if response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            st.code(response.text)
            return

        data = parse_n8n_response(response.json())
        st.code(data)
        print(f"Data from response: {data}")
        if data is None:
            return
        else:
            st.session_state["extracted_jd_status"] = True

        st.session_state["extracted_jd"] = data
        st.session_state["user_input"] = user_inp
        st.success("Extracted successfully!")


def generate_questions_section(jd_data):
    """Placeholder for later — uses saved extracted data."""
    st.divider()
    print(f"generating questions------->")
    if jd_data==None:
        st.error(f"Job Description extraction was not done, please retry.")
        return
    
    if st.button("Generate Interview Questions"):
        with st.spinner("Generating question… \nthis may take 10-20 seconds"):
            try:
                print(f"Request sent to /questions----------->")
                question_response = requests.post(f"{WEBHOOK_URL}/questions", json=jd_data, timeout=60)
                print(f"Got response from /questions----------->")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection failed: {e}")
                st.info("Check if n8n is running and you clicked 'Execute workflow' on the canvas.")
                return
        if question_response!=None:
            print(f"Q Data---> {question_response.text}")
            q_data=parse_n8n_response(question_response.json())
            st.session_state["question_data"]=q_data
            print(f"Q Data---> {q_data}")
            st.success("Questions Data Generated properly ❤️")
            st.write(q_data)
            
        else:
            return

def extract_questions(q_data):
    if isinstance(q_data, list) and len(q_data) > 0:
        q_data = q_data[0]

    if isinstance(q_data, dict):
        return q_data.get("questions", [])

    return []

def display_questions_section():
    if "question_data" not in st.session_state:
        return

    questions = extract_questions(st.session_state["question_data"])

    if not questions:
        st.warning("No questions found.")
        return

    if "answers_submitted" not in st.session_state:
        st.session_state["answers_submitted"] = False

    if "answers" not in st.session_state:
        st.session_state["answers"] = {}

    st.divider()
    st.subheader("Interview Questions")

    for i, q in enumerate(questions, start=1):
        q_id = q.get("id", f"q{i}")

        with st.container(border=True):
            st.markdown(f"### Q{i}. {q.get('question', 'No question text')}")
            st.caption(
                f"Category: {q.get('category', 'N/A')} | "
                f"Focus: {q.get('focus_area', 'N/A')} | "
                f"Depth: {q.get('expected_depth', 'N/A')}"
            )

            answer = st.text_area(
                "Your answer",
                key=f"answer_{q_id}",
                height=130,
                disabled=st.session_state["answers_submitted"]
            )

            st.session_state["answers"][q_id] = {
                "question_id": q_id,
                "question": q.get("question"),
                "category": q.get("category"),
                "focus_area": q.get("focus_area"),
                "expected_depth": q.get("expected_depth"),
                "ideal_answer_points": q.get("ideal_answer_points", []),
                "answer": answer
            }

            # Locked until submitted
            if st.session_state["answers_submitted"]:
                with st.expander("Ideal answer points"):
                    for point in q.get("ideal_answer_points", []):
                        st.markdown(f"- {point}")

    if not st.session_state["answers_submitted"]:
        if st.button("Submit Answers"):
            answered = [
                a for a in st.session_state["answers"].values()
                if a["answer"].strip()
            ]

            if not answered:
                st.error("Please answer at least one question before submitting.")
                return

            st.session_state["submitted_answers"] = answered
            st.session_state["answers_submitted"] = True
            st.success("Answers submitted. Ideal answer points are now unlocked.")
            st.rerun()

    else:
        st.success("Answers are submitted and locked.")

        if st.button("Show Evaluation"):
            run_evaluation()

def run_evaluation():
    payload = {
        "user_id": "demo_user",
        "jd_data":st.session_state.get("extracted_jd", []),
        "answers": st.session_state.get("submitted_answers", [])
    }

    with st.spinner("Evaluating your answers..."):
        try:
            evaluation_response = requests.post(f"{WEBHOOK_URL}/evaluate", json=payload, timeout=120)
        except requests.exceptions.RequestException as e:
            st.error(f"Evaluation request failed: {e}")
            return

    if response.status_code != 200:
        st.error(f"Evaluation failed: {evaluation_response.status_code}")
        st.code(evaluation_response.text)
        return

    st.session_state["evaluation_result"] = response.json()

def display_evaluation_section():
    if "evaluation_result" not in st.session_state:
        return

    result = st.session_state["evaluation_result"]

    st.divider()
    st.subheader("Evaluation Result")

    if isinstance(result, list) and result:
        result = result[0]

    st.json(result)

    evaluations = result.get("evaluations", [])
    overall_score = result.get("overall_score")
    weak_areas = result.get("weak_areas", [])
    strength_areas = result.get("strength_areas", [])

    if overall_score is not None:
        st.metric("Overall Score", overall_score)

    if weak_areas:
        st.subheader("Weak Areas")
        for area in weak_areas:
            st.markdown(f"- {area}")

    if strength_areas:
        st.subheader("Strength Areas")
        for area in strength_areas:
            st.markdown(f"- {area}")

    if evaluations:
        st.subheader("Per Question Feedback")
        for ev in evaluations:
            with st.container(border=True):
                st.markdown(f"**Question ID:** {ev.get('question_id')}")
                st.metric("Score", ev.get("score", "N/A"))
                st.write(ev.get("feedback", ""))
                st.warning(f"Weak area: {ev.get('weak_area', 'N/A')}")
                st.info(ev.get("improvement_tip", ""))

def main():
    welcome()
    user_input_form()

    if "extracted_jd" in st.session_state:
        display_extracted_data(st.session_state["extracted_jd"])
        generate_questions_section(st.session_state["extracted_jd"])
        display_questions_section()
        display_evaluation_section()

if __name__ == "__main__":
    main()
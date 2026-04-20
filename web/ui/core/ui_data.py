import streamlit as st
import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = "http://localhost:5678/webhook-test/gather"
MISTRAL_KEY = os.getenv("MISTRAL_KEY")


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
        st.error("Couldn't find LLM output in the response. Check the expander above to see the actual structure.")
        return None

    # Strip markdown code fences and parse
    cleaned = re.sub(r"```json|```", "", raw_text).strip()
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
                response = requests.post(WEBHOOK_URL, json=user_inp, timeout=60)
            except requests.exceptions.RequestException as e:
                st.error(f"Connection failed: {e}")
                st.info("Check if n8n is running and you clicked 'Execute workflow' on the canvas.")
                return

        if response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            st.code(response.text)
            return

        data = parse_n8n_response(response.json())
        if data is None:
            return

        st.session_state["extracted_jd"] = data
        st.session_state["user_input"] = user_inp
        st.success("Extracted successfully!")


def generate_questions_section():
    """Placeholder for later — uses saved extracted data."""
    if "extracted_jd" not in st.session_state:
        return

    st.divider()
    if st.button("Generate Interview Questions (coming next)"):
        st.info("This will use the extracted data above to generate tailored questions.")


def main():
    welcome()
    user_input_form()

    if "extracted_jd" in st.session_state:
        display_extracted_data(st.session_state["extracted_jd"])
        generate_questions_section()


if __name__ == "__main__":
    main()
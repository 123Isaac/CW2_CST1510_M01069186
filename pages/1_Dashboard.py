import streamlit as st
from datetime import datetime
from app.data.db import DB_PATH, connect_database
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
import os
import csv
from google import genai
from dotenv import load_dotenv
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not st.session_state.logged_in:
    st.error("Please log in to access the Dashboard.")
    if st.button("Go to Login Page"):
        st.switch_page("home.py")
        st.stop()
else:
    # Load .env and prefer GENAI_API_KEY
    load_dotenv()
    apikey = os.getenv("GENAI_API_KEY")
    if not apikey:
        st.error("GENAI_API_KEY not found in environment variables. Please set it to use AI features.")

    client = genai.Client(api_key=apikey)
    st.set_page_config(page_title="Dashboard", layout="wide")
    st.title("Dashboard")
    
    conn = connect_database()
    incidents = get_all_incidents(conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        #Account statistics
        st.subheader("Total Incidents Reported by You")
        user_incidents = incidents[incidents['reported_by'] == st.session_state.username]
        st.metric("Total Incidents", len(user_incidents))
    with col2:
        #Account Role
        st.subheader("Role")
        st.metric("User Role", st.session_state.role)
    with col3:
        #AI Bot Interaction
        st.subheader("AI Bot Interaction")
        user_input = st.text_input("Ask the AI Bot a question about incidents:")
        if st.button("Submit Question"):
            if user_input.strip() == "":
                st.warning("Please enter a question.")
            else:
                # Build contents: system instruction, chat history, incidents sample, and the user prompt
                try:
                    # System instruction: cyber incident management assistant
                    system_instruction = (
                        "You are a Cyber Incident Management AI. Assist with triage, summarization, prioritization, "
                        "and recommending next actions for cyber incidents. Be concise, factual, and avoid fabricating data. "
                        "The incidents database is included below for reference — DO NOT reference or cite it unless the user explicitly requests you to do so. "
                        "If asked to reference incidents, cite rows/fields exactly as provided."
                    )

                    # Recent chat history from session state
                    session_lines = []
                    for q, a in st.session_state.chat_history[-10:]:
                        session_lines.append(f"Q: {q}\nA: {a}")
                    session_chat = "\n---\n".join(session_lines) if session_lines else "(no recent chat history)"

                    # Also include last 10 lines from DATA/message_history.csv if present
                    from pathlib import Path
                    project_root = Path(__file__).resolve().parents[1]
                    msg_path = project_root / "DATA" / "message_history.csv"
                    file_chat = "(no chat history file)"
                    try:
                        if msg_path.exists():
                            with msg_path.open(newline="", encoding="utf-8") as mf:
                                import csv as _csv
                                rows = list(_csv.reader(mf))
                            if rows:
                                last = rows[-10:]
                                lines = []
                                for r in last:
                                    if len(r) >= 3:
                                        timestamp, role, msg = r[0], r[1], r[2]
                                    elif len(r) == 2:
                                        timestamp, role = r[0], r[1]
                                        msg = ""
                                    else:
                                        timestamp = ""
                                        role = "unknown"
                                        msg = ",".join(r)
                                    lines.append(f"{timestamp} [{role}]: {msg}")
                                file_chat = "\n".join(lines)
                    except Exception:
                        file_chat = "(could not read message_history.csv)"

                    # Sample incidents: use DataFrame `incidents` (from get_all_incidents)
                    try:
                        if incidents is None or len(incidents) == 0:
                            incidents_sample = "(incidents DB appears empty)"
                        else:
                            incidents_sample = incidents.head(10).to_csv(index=False)
                    except Exception:
                        incidents_sample = "(could not sample incidents)"

                    # Compose full contents
                    full_contents = (
                        "SYSTEM INSTRUCTION:\n" + system_instruction + "\n\n"
                        + "SESSION CHAT HISTORY (most recent):\n" + session_chat + "\n\n"
                        + "FILE CHAT HISTORY (message_history.csv last lines):\n" + file_chat + "\n\n"
                        + "INCIDENTS DATABASE (included for reference; DO NOT REFERENCE UNLESS ASKED):\n" + incidents_sample + "\n\n"
                        + "USER PROMPT:\n" + user_input
                    )

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=full_contents,
                    )
                    answer = getattr(response, "text", str(response))
                    # save to session chat history
                    st.session_state.chat_history.append((user_input, answer))
                except Exception as e:
                    st.error(f"API call failed: {e}")

    st.divider()
    st.subheader("AI Chat History")
    for question, answer in st.session_state.chat_history:
        st.markdown(f"**Q:** {question}")
        st.markdown(f"**A:** {answer}")
        st.markdown("---")
    st.divider()
    #
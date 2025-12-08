import streamlit as st
from datetime import datetime
from app.data.db import DB_PATH, connect_database
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
import os
import csv
from google import genai
from dotenv import load_dotenv

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "auto_save_history" not in st.session_state:
    st.session_state.auto_save_history = True


def _persist_message(role: str, text: str, persist_path: str):
    os.makedirs(os.path.dirname(persist_path), exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with open(persist_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, role, text])

if not st.session_state.logged_in:
    st.error("Please log in to access the Dashboard.")
    if st.button("Go to Login Page"):
        st.switch_page("main.py")
        st.stop()
else:
    st.title("Dashboard")
    st.success(f"Welcome, {st.session_state.username}! You are logged in as '{st.session_state.get('role', 'user')}'.")
    
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

client = genai.Client(api_key=GENAI_API_KEY)

prompt = st.text_area("Enter your query for the Cyber Incident Management System:")

# persisted history CSV path
persist_path = os.path.join(os.getcwd(), "DATA", "message_history.csv")

if st.button("Get AI Response"):
    if prompt.strip() == "":
        st.error("Please enter a valid query.")
    else:
        # append user message to session history and optionally persist
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        if st.session_state.auto_save_history:
            try:
                _persist_message("user", prompt, persist_path)
            except Exception:
                # don't fail the chat on persistence errors
                pass

        with st.spinner("Generating response..."):
            contents = [
                {"text": "You are an expert assistant for the Cyber Incident Management System."},
                {"text": prompt}
            ]

            full_text = ""
            try:
                response_stream = client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    contents=contents
                )

                for chunk in response_stream:
                    # stream chunk shapes vary; try common attributes
                    if hasattr(chunk, "text") and chunk.text:
                        full_text += chunk.text
                    elif hasattr(chunk, "output_text") and chunk.output_text:
                        full_text += chunk.output_text
                    elif hasattr(chunk, "delta") and chunk.delta:
                        # some stream shapes use delta
                        full_text += str(chunk.delta)
            except Exception as e:
                # detect token/quota related issues and render a friendly message
                msg = str(e).lower()
                token_indicators = ["token", "quota", "insufficient", "exhausted", "no more tokens", "quota exceeded", "insufficient_quota", "insufficient_tokens"]
                if any(ind in msg for ind in token_indicators):
                    full_text = "The AI system is currently unavailable (out of tokens or quota). Please try again later."
                else:
                    full_text = "The AI system is currently unavailable. Please try again later."

        # append assistant message and persist if enabled
        st.session_state.chat_history.append({"role": "assistant", "content": full_text})
        if st.session_state.auto_save_history:
            try:
                _persist_message("assistant", full_text, persist_path)
            except Exception:
                pass

        st.markdown("### AI Response:")
        st.write(full_text)

    
    st.divider()
    
    # show chat history
    with st.expander("Chat History", expanded=False):
        if not st.session_state.chat_history:
            st.info("No messages yet.")
        else:
            for msg in st.session_state.chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "assistant":
                    st.code(content)
                elif role == "system":
                    st.caption(content)
                else:
                    st.write(f"**You:** {content}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("You have been logged out.")
        st.switch_page("main.py")
    
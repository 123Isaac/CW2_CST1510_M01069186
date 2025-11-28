import streamlit as st
from datetime import date
from app.data.db import DB_PATH, connect_database
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident

conn = connect_database()

st.title("Incidents Dashboard")
    
incidents = get_all_incidents(conn)
st.dataframe(incidents, use_container_width=True)

with st.form("Add Incident"):
    title=st.text_input("Incident Title")
    severity=st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    status=st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
    
    submitted=st.form_submit_button("Add Incident")
    if submitted and title:
        insert_incident(conn,date.today(),title,severity,status,)
        st.success(f"Incident '{title}' added successfully!")
        st.rerun()    
conn.close()
import streamlit as st
from datetime import date
from app.data.db import DB_PATH, connect_database
from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident

st.set_page_config(page_title="Incidents Dashboard", layout="wide")

st.title("Incidents Dashboard")

    
if not st.session_state.logged_in:
    st.error("Please log in to access the Incidents Dashborad.")
    if st.button("Go to Login Page"):
        st.switch_page("home.py")
        st.stop()
else:
    conn = connect_database()
    incidents = get_all_incidents(conn)
    col1, col2,col3 = st.columns(3)
    with col1:
        st.subheader("Incidents by Type")
        st.line_chart(incidents['incident_type'].value_counts())
    with col2:
        st.subheader("Incidents by Severity")
        st.area_chart(incidents['severity'].value_counts())
    with col3:
        st.subheader("Reported Incidents by Users")
        st.bar_chart(incidents['reported_by'].value_counts())
        
    st.dataframe(incidents, use_container_width=True, height=400)
    
    
    with st.form("Update Incident"):
        incident_ids = incidents["id"].tolist()
        selected_id = st.selectbox("Select Incident ID to Update", incident_ids)
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
        
        submitted = st.form_submit_button("Update Status")
        if submitted:
            rows_updated = update_incident_status(conn, selected_id, new_status)
            if rows_updated:
                st.success(f"Incident ID {selected_id} status updated to '{new_status}'")
                st.rerun()
            else:
                st.error("Failed to update incident status.")
        
        delete_submitted = st.form_submit_button("Delete Incident")
        if delete_submitted:
            rows_deleted = delete_incident(conn, selected_id)
            if rows_deleted:
                st.success(f"Incident ID {selected_id} deleted successfully.")
                st.rerun()
            else:
                st.error("Failed to delete incident.")

    with st.form("Add Incident"):
        title=st.text_input("Incident Title")
        severity=st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        type=st.selectbox("Type", ["Network", "Hardware", "Software", "Security", "Other"])
        status=st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        description=st.text_area("Description")
        
        submitted=st.form_submit_button("Add Incident")
        if submitted and title:
            insert_incident(
                conn,
                date.today().isoformat(),
                title,
                severity,
                status,
                description,
                st.session_state.username
            )
            st.success(f"Incident '{title}' added successfully!")
            st.rerun()    
    conn.close()
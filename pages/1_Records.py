import streamlit as st
from datetime import date
st.title("Records Management")
if st.session_state.get("role")!="admin":
    st.error("Access denied. Admins only.")
else:
    if st.session_state.get("role") == "admin":
        st.info("You have admin privileges.")
        st.header("Manage Records")
        if "records" not in st.session_state:
            st.session_state.records = []
        
        if st.session_state.records:
            import pandas as pd
            df = pd.DataFrame(st.session_state.records)
            st.dataframe(df, use_container_width=True)
            names = [record["name"] for record in st.session_state.records]
            selected_name = st.selectbox("Select a record to Update", names)
            idx = names.index(selected_name)
            record = st.session_state.records[idx]
            st.markdown("### Update Record")
            with st.form("update_record"):
                new_name = st.text_input("Record Name", value=record["name"])
                new_email = st.text_input("Record Email", value=record["email"])
                new_role = st.selectbox("Record Role", ["user", "admin"], index=["user", "admin"].index(record["role"]))
                if st.form_submit_button("Update Record"):
                    st.session_state.records[idx] = {"name": new_name, "email": new_email, "role": new_role}
                    st.success(f"Record '{new_name}' updated successfully!")
            to_delete = st.button(f"Delete Record '{selected_name}'")
            col1, col2 = st.columns([1,1])
            with col2:
                st.warning(f"Are you sure you want to delete record '{selected_name}'?")
            with col1:
                if to_delete:
                    st.session_state.records.pop(idx)
                    st.success(f"Record '{selected_name}' deleted successfully!")
                    st.rerun()
            
            
        else:
            st.info("No records available.")
        
        
        st.subheader("Add New Record")
        with st.form("add_record"):
            name = st.text_input("Record Name")
            email = st.text_input("Record Email")
            role = st.selectbox("Record Role", ["user", "admin"])
        
            if st.form_submit_button("Add Record"):
                record = {"name": name, "email": email, "role": role}
                st.session_state.records.append(record)
                st.success(f"Record '{name}' added successfully!")
        

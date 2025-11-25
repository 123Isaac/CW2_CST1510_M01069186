import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """
    Insert a new cyber incident into the database.
    
    TODO: Implement this function following the register_user() pattern.
    
    Args:
        conn: Database connection
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident
        severity: Severity level
        status: Current status
        description: Incident description
        reported_by: Username of reporter (optional)
        
    Returns:
        int: ID of the inserted incident
    """
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO cyber_incidents (date, incident_type, severity, status, description, reported_by) VALUES (?, ?, ?, ?, ?, ?)",
        (date, incident_type, severity, status, description, reported_by)
    )
    conn.commit()
    
    return cursor.lastrowid

def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.
    
    TODO: Implement using pandas.read_sql_query()
    
    Returns:
        pandas.DataFrame: All incidents
    """
    return pd.read_sql_query("SELECT * FROM cyber_incidents", conn)

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    
    TODO: Implement UPDATE operation.
    """
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    conn.commit()
    
    return cursor.rowcount

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    TODO: Implement DELETE operation.
    """
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM cyber_incidents WHERE id = ?",
        (incident_id,)
    )
    conn.commit()
    
    return cursor.rowcount
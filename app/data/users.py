from app.data.db import connect_database

def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def insert_user(username, password_hash, role='user'):
    """Insert new user."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()
    
def get_role_by_username(username):
    """Retrieve user role by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
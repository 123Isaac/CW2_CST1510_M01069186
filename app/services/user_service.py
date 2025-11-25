import sqlite3
import bcrypt
import pandas as pd
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table

DATA_DIR = Path("DATA")

def register_user(username, password, role="user"):
    """
    Register a new user in the database.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    
    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."
    
    # Hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()
    
    return True, f"User '{username}' registered successfully!"

def login_user(username, password):
    """
    Authenticate a user against the database.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    
    Args:
        username: User's login name
        password: Plain text password to verify
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    # Find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return False, "Username not found."
    
    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."

def migrate_users_from_file(conn, filepath=DATA_DIR/"users.txt"):
    """
    Migrate users from users.txt to the database.
    
    This is a COMPLETE IMPLEMENTATION as an example.
    
    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return
    
    cursor = conn.cursor()
    migrated_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]
                
                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")
    
def verfiy_migration(conn):
    # Verify users were migrated
    cursor = conn.cursor()

    # Query all users
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    print(" Users in database:")
    print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
    print("-" * 35)
    for user in users:
        print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

    print(f"\nTotal users: {len(users)}")
    
def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    
    TODO: Implement this function.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table
        
    Returns:
        int: Number of rows loaded
    """
    csv_path = Path(csv_path)
    
    # Check if CSV file exists
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return 0
    
    # Read CSV using pandas
    df = pd.read_csv(csv_path)
    
    # Use df.to_sql() to insert data
    row_count = len(df)
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    
    # Print success message and return row count
    print(f"✅ Loaded {row_count} rows into {table_name} from {csv_path.name}")
    return row_count
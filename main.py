import bcrypt
import os

USER_DATA_FILE = "users.txt"

def hash_password(plain_text_password: str) -> str:
    password_bytes = plain_text_password.encode('utf-8')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    # Decode the hash back to a string to store in a text file
    return hashed_password.decode('utf-8')

def verify_password(plain_text_password: str, stored_hash: str) -> bool:
    # Encode both the plaintext password and the stored hash to bytes
    password_bytes = plain_text_password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')
    # Use bcrypt.checkpw() to verify the password
    return bcrypt.checkpw(password_bytes, stored_hash_bytes)

def register_user(username: str, password: str) -> bool:
    """Register a new user if the username is not already taken."""
    if user_exists(username):
        print("Username already exists.")
        return False
    hashed = hash_password(password)
    # Append the new user to the file
    with open(USER_DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username},{hashed}\n")
    print("Registering new user.")
    return True

def user_exists(username: str) -> bool:
    """Return True if a user with the given username exists."""
    if not os.path.exists(USER_DATA_FILE):
        return False
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue
            stored_username = parts[0]
            if stored_username == username:
                return True
    return False

def login_user(username: str, password: str) -> bool:
    """Attempt to login a user by verifying the password against stored hash."""
    if not os.path.exists(USER_DATA_FILE):
        print("No users registered yet.")
        return False
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue
            stored_username, stored_hashed_password = parts[0], parts[1]
            if stored_username == username:
                if verify_password(password, stored_hashed_password):
                    print("Login successful.")
                    return True
                else:
                    print("Incorrect password.")
                    return False
    print("Username not found.")
    return False

def validate_username(username):
    # TODO: Implement username validation logic
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not username.isalnum():
        return False, "Username must be alphanumeric."
    return True, ""

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    return True, ""

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()
            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            register_user(username, password)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
                print("(In a real application, you would now access the dashboard or secure resources.)")

            # Optional: Ask if they want to logout or exit
            input("\nPress Enter to return to main menu...")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
# This code implements a simple user authentication system with registration and login functionalities.
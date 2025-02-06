import streamlit as st
import csv
import os
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager

# Load environment variables
load_dotenv()
TOKEN_VALID_DAYS = int(os.getenv("TOKEN_VALID_DAYS", "7"))
COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD", "default_password")
USERS_CSV = "users.csv"
TOKENS_CSV = "tokens.csv"

# Initialize cookies manager
cookies = EncryptedCookieManager(prefix="auth_", password=COOKIE_PASSWORD)
if not cookies.ready():
    st.stop()

# Helper functions
def load_users():
    """Load valid users from CSV."""
    users = {}
    try:
        with open(USERS_CSV, "r") as f:
            reader = csv.reader(f)            
            for row in reader:
                if row and len(row) >= 2:
                    email, active = row[0].strip(), row[1].strip().lower()                    
                    users[email] = active == "1"
    except FileNotFoundError:
        st.error(f"CSV file {USERS_CSV} not found!")
    return users


def compute_token(email, expiry_date_str):
    """Generate a secure token."""
    token_str = email + expiry_date_str
    return hashlib.sha256(token_str.encode()).hexdigest()


def generate_expiry_date():
    """Generate an expiry date string."""
    return (datetime.now() + timedelta(days=TOKEN_VALID_DAYS)).strftime("%d%m%Y")


def store_token(email, token, expiry_date):
    """Store token in CSV."""
    with open(TOKENS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email, token, expiry_date])


def validate_token(token):
    """Check if token is valid."""
    try:
        with open(TOKENS_CSV, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3 and row[1] == token:
                    expiry_date = datetime.strptime(row[2], "%d%m%Y")
                    return datetime.now() <= expiry_date
    except FileNotFoundError:
        return False
    return False


def login_flow(users):
    """Login form."""
    st.header("Login")
    email = st.text_input("Enter your email:")
    if st.button("Submit"):
        email = email.strip()
        if email in users and users[email]:
            expiry_date = generate_expiry_date()
            token = compute_token(email, expiry_date)
            store_token(email, token, expiry_date)
            cookies["auth_token"] = token
            cookies.save()
            st.success("Login successful! Reloading...")
            st.rerun()
        else:
            st.error("Invalid or inactive email.")

def remove_token_from_csv(token_to_remove):
    """Remove all occurrences of a token from the tokens CSV file."""
    if not os.path.exists(TOKENS_CSV):
        return  # No file, nothing to remove

    with open(TOKENS_CSV, "r") as f:
        rows = [row for row in csv.reader(f) if len(row) >= 2 and row[1] != token_to_remove]

    with open(TOKENS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def logout():
    """Handles user logout by removing token from CSV and cookies."""
    token = cookies.get("auth_token")
    if token:
        remove_token_from_csv(token)  # Delete from CSV
        del cookies["auth_token"]  # Delete cookie
        cookies.save()
        st.success("Logged out successfully!")
        st.rerun()

def protected_content():
    """Display protected content with logout option."""
    st.header("Protected Content")
    st.write("Welcome to the secured area!")

    # Logout button
    if st.button("Logout"):
        logout()


def main():
    users = load_users()
    token = cookies.get("auth_token")
    if token and validate_token(token):
        protected_content()
    else:
        login_flow(users)


if __name__ == "__main__":
    main()

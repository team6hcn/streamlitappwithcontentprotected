import streamlit as st
import csv
import os
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from streamlit_cookies_manager import EncryptedCookieManager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

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


def send_login_email(email, token, expiry_date):
    """Send login email with a crypted link."""
    base_url = os.getenv("BASE_URL")
    creation_date = datetime.now().strftime("%d%m%Y")
    hash_str = f"{email}{token}{expiry_date}{creation_date}"
    encrypted_link = base64.urlsafe_b64encode(hash_str.encode()).decode()

    # Use a query parameter instead of a path-based route
    login_url = f"{base_url}/?verify={encrypted_link}"

    subject = "Login Link"
    body = f"Click the following link to log in: {login_url}"
    
    sender_email = os.getenv("SMTP_USER")
    receiver_email = email
    password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Login email sent to {email} with link: {login_url}")  # Debugging
    except Exception as e:
        print(f"===========================>")
        print(f"Login email sent to {email} with link: {login_url}")
        print(f"Error sending email: {e}")


def verify_login_link(encrypted_link):
    """Verify login link and set cookie if valid."""
    try:
        print(f"encrypted_link : {encrypted_link}")
        decoded_link = base64.urlsafe_b64decode(encrypted_link).decode()
        print(f"decoded_link : {decoded_link}")

        # Extract email first
        email_end = decoded_link.find("@") + decoded_link[decoded_link.find("@"):].find(".") + 4  # Find end of email
        email = decoded_link[:email_end]
        token = decoded_link[email_end:email_end+64]  # SHA-256 is 64 chars
        expiry_date = decoded_link[email_end+64:email_end+72]
        creation_date = decoded_link[email_end+72:]

        print(f"email : {email}")
        print(f"token : {token}")
        print(f"expiry_date : {expiry_date}")
        print(f"creation_date : {creation_date}")
        
        if datetime.now() > datetime.strptime(expiry_date, "%d%m%Y"):
            return False  # Token expired

        # Set cookie and store token
        cookies["auth_token"] = token
        cookies.save()
        store_token(email, token, expiry_date)  # ✅ Now, email is correctly defined!
        return True
    except Exception as e:
        print(f"Error verifying link: {e}")
        return False


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
            send_login_email(email, token, expiry_date)
            st.success("Login successful! Please check your email to verify.")
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

    # Check if the app was accessed with a verification query parameter
    query_params = st.query_params  # New method in Streamlit >1.23
    if "verify" in query_params:
        encrypted_link = query_params["verify"]
        if verify_login_link(encrypted_link):
            st.success("Successfully logged in! You can now access your dashboard.")
            #st.rerun()
            del st.query_params["verify"]
            # JavaScript for redirection after 3 seconds
            base_url = os.getenv("BASE_URL", "http://localhost:8501")
            st.markdown(f"[Go to Dashboard]({base_url})")
        else:
            st.error("Invalid or expired link.")

    elif token and validate_token(token):
        protected_content()
    else:
        login_flow(users)



if __name__ == "__main__":
    main()

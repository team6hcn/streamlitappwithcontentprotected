
# Streamlit Authentication App

This is a simple Streamlit application that implements email-based login and token-based authentication. The app securely stores tokens in a CSV file and uses encrypted cookies to manage sessions.

## Features

- **Email-based login:** Users log in using their email address.
- **Token-based authentication:** Tokens are generated, stored, and validated to ensure secure access.
- **Encrypted cookies:** Session tokens are stored in encrypted cookies for added security.
- **Protected content:** Only authenticated users can access the protected area of the app.
- **Logout functionality:** Users can log out, which removes their token from the CSV file and the cookies.
- 
![image](https://github.com/user-attachments/assets/cbadbb29-a83d-4f85-bf14-267b56546954)
![image](https://github.com/user-attachments/assets/ff012889-5d76-46e7-93ff-6eaf4699750f)

## Requirements

- Python 3.x
- Streamlit
- `python-dotenv` for loading environment variables
- `streamlit_cookies_manager` for encrypted cookie management
- **TODO:** Add SMTP email functionality to send confirmation emails upon login or other events.

## Setup

1. **Install dependencies:**

   Ensure that you have the necessary Python libraries installed. You can install them using `pip`:

   ```bash
   pip install streamlit streamlit-cookies-manager python-dotenv
   ```

2. **Create a `.env` file:**

   Create a `.env` file in the root directory of the project with the following variables:

   ```
   TOKEN_VALID_DAYS=7
   COOKIE_PASSWORD=your_cookie_password
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   SMTP_USER=your_email@example.com
   SMTP_PASSWORD=your_smtp_password
   ```

   - `TOKEN_VALID_DAYS`: The number of days a token is valid for. Default is 7 days.
   - `COOKIE_PASSWORD`: A password used to encrypt the cookies. Make sure to choose a secure password.
   - **TODO:** Add SMTP configuration to send emails for events like login notifications.

3. **Prepare the users and tokens CSV files:**

   Create a `users.csv` file to store the user emails and their activation status. The file should have the following format:

   ```
   email@example.com, 1
   user2@example.com, 1
   ```

   - The first column is the user’s email.
   - The second column represents whether the user is active (`1` for active, `0` for inactive).

   The `tokens.csv` file will be automatically generated when a user logs in, storing their token and its expiry date.

4. **Run the application:**

   To start the Streamlit app, run the following command:

   ```bash
   streamlit run app.py
   ```

   Replace `app.py` with the name of your Python script if different.

## How it Works

### Authentication Flow

1. **Login:**
   - When the app starts, users are prompted to enter their email address.
   - If the email is valid and active (from `users.csv`), a token is generated, stored in `tokens.csv`, and saved in an encrypted cookie.

2. **Protected Content:**
   - After login, the user is granted access to protected content. If the session is valid, they can access the protected area.

3. **Logout:**
   - The user can log out, which will remove the session token both from the CSV file and the encrypted cookies.

### Functions

- **`load_users()`**: Loads the list of users from `users.csv` and checks if they are active.
- **`compute_token()`**: Generates a secure token using the email and an expiry date.
- **`generate_expiry_date()`**: Generates an expiry date for the token.
- **`store_token()`**: Saves the generated token to `tokens.csv`.
- **`validate_token()`**: Validates the token by checking if it exists in `tokens.csv` and if it has not expired.
- **`login_flow()`**: Handles the user login flow, including form input and token generation.
- **`logout()`**: Logs the user out by removing the token from both the CSV file and cookies.
- **`protected_content()`**: Displays the protected content and provides an option to log out.
- **`main()`**: The main entry point of the app that manages the user authentication flow.

---

## How to Implement This Code

1. **Download the code**:
   - Save the Python code to a file (e.g., `app.py`) in your project directory.

2. **Configure environment variables**:
   - Create a `.env` file to set the `TOKEN_VALID_DAYS`, `COOKIE_PASSWORD`, and SMTP configuration as described in the setup section.

3. **Create the `users.csv` file**:
   - This file contains the email addresses of users and their active status (1 for active, 0 for inactive).
   - Ensure that the file is in the same directory as your Python script.

4. **Run the app**:
   - After setting up everything, run the Streamlit app with the following command:

     ```bash
     streamlit run app.py
     ```

5. **Access the app**:
   - Open the browser to the URL provided by Streamlit (usually `http://localhost:8501`).
   - The app will prompt you for your email and either log you in or show an error if the email is invalid or inactive.

---

## Troubleshooting

- **CSV File Not Found**: Make sure the `users.csv` file exists and is correctly formatted.
- **Invalid Token**: Ensure that the session token has not expired. If the token has expired, the user will be prompted to log in again.
- **Cookie Issues**: Clear your browser cookies if you encounter any issues with the encrypted cookies.


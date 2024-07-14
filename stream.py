import joblib
import streamlit as st
import speech_recognition as sr
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mysqlconnection import register, login, insert_post, get_post
import os
from dotenv import load_dotenv

load_dotenv()

sender = os.environ.get('senderEmail')
receiver = os.environ.get('receiverEmail')
password_email = os.environ.get('password')

# Load the trained model
file_name = "finalized_model.sav"
loaded_model = joblib.load(file_name)

sender_email = sender
receiver_email = receiver
password = password_email

message = MIMEMultipart("alternative")
message["Subject"] = "Alert!!"
message["From"] = sender_email
message["To"] = receiver_email

# Construct the email message
text = f"""\
Hi,

"""
if "username" in st.session_state:
    text += f"{st.session_state.username} seems to be very depressed.\nPlease contact him/her."
else:
    text += "A user seems to be very depressed.\nPlease contact him/her."

part1 = MIMEText(text, "plain")
message.attach(part1)

# Define custom CSS styles
custom_css = """
<style>
body {
    background-color: #000000  ; /* Change this to your desired background color */
}
</style>
"""

# Render the custom CSS styles
st.markdown(custom_css, unsafe_allow_html=True)

# Function to check login credentials
def authenticate(username, password):
    return login(username, password)

# Login page
def login_page():
    st.title("Mindful Threads")
    st.title("Login")
    st.markdown("Already have an account? Log in below.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        def handle_login_result(success):
            if success:
                st.session_state.username = username
                st.session_state.page = "main"
                st.session_state.user_posts = []  # Initialize an empty list to store user posts
            else:
                st.error("Invalid username or password.")
        login(username, password, handle_login_result)
    st.markdown("---")
    st.markdown("Don't have an account? Sign up below.")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Sign up"):
        def handle_registration_result(success):
            if success:
                st.session_state.username = new_username
                st.session_state.page = "main"
                st.session_state.user_posts = []  # Initialize an empty list to store user posts
            else:
                st.error("Registration failed. Please try again.")
        register(new_username, new_password, "", handle_registration_result)


# Main content page
# Main content page
def main():
    if "is_listening" not in st.session_state:
        st.session_state.is_listening = False  # Initialize is_listening attribute

    if "recorded_text" not in st.session_state:
        st.session_state.recorded_text = ""  # Initialize recorded_text attribute

    st.title(f"Welcome to Mindful Threads, {st.session_state.username}!")
    st.title("Type your mind here.")
    st.markdown("You can start describing your day, how you're feeling, etc.")

    # removing the streamlit banner at the bottom
    hide_streamlit_style = """
                <style>
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Speech input button
    if st.button("Give a small Talk (6 Sec)"):
        st.session_state.is_listening = True
        st.session_state.recorded_text = ""

    if st.session_state.is_listening:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Adjusting noise ")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Recording for 6 seconds")
            recorded_audio = recognizer.listen(source, timeout=6)
            print("Done recording")

        try:
            print("Recognizing the text")
            text = recognizer.recognize_google(
                recorded_audio, 
                language="en-US"
            )
            st.session_state.recorded_text = text
            print("Decoded Text : {}".format(text))

        except Exception as ex:
            print(ex)
            st.write("Error occurred during speech recognition.")

    # Text input area
    text = st.text_input("Text", key="user_text", value=st.session_state.recorded_text)
    if text:
        if "user_posts" not in st.session_state:
            st.session_state.user_posts = []
        st.session_state.user_posts.append(text)  # Store the text in session state
        if len(st.session_state.user_posts) > 10:
            st.session_state.user_posts = st.session_state.user_posts[-10:]  # Keep only the last 10 posts
        # Display the last 10 posts made by the user
        st.write(f"Posts by {st.session_state.username}:")
        for post in st.session_state.user_posts:
            st.write(post)
        result = loaded_model.predict([text])[0]  # Get the prediction result

        if result == 'suicide':
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )

        # Insert post into database
        insert_post(st.session_state.username, text, result)
        
        # Display the prediction result in the terminal
        print(f"Prediction for '{text}': {result}")
        # Don't display the prediction result to the user

    # Display posts from the database
    st.title("Recent Posts")
    get_post(display_posts)

# Function to display posts
def display_posts(posts):
    for post in posts:
        st.write(f"Author: {post['username']}")
        st.write(f"Post: {post['post']}")
        st.write(f"Posted at: {post['posted_at']}")
        st.markdown("---")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"

# Render the appropriate page based on the session state
if st.session_state.page == "login":
    login_page()    
elif st.session_state.page == "main":
    main()


#python -m streamlit run stream.py
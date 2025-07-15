import streamlit as st
import requests
from dotenv import load_dotenv
import os
import io
from PIL import Image
import speech_recognition as sr
import base64
import json

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


# Constants
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("🤖 Mistral Chatbot (via Together.ai)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_dark_mode():
    if st.session_state.dark_mode:
        st.write('<style>body { background-color: #333; color: white; }</style>', unsafe_allow_html=True)
    else:
        st.write('<style>body { background-color: #fff; color: black; }</style>', unsafe_allow_html=True)

toggle_dark_mode()

uploaded_file = st.file_uploader("📁 Upload a text file or image (jpg, png, jpeg, pdf)", type=["txt", "pdf", "jpg", "png", "jpeg"])

def transcribe_audio(file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
    except Exception as e:
        return f"[Error transcribing audio: {e}]"

def show_chat_history():
    st.markdown("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

def voice_input_button():
    mic_button = st.button("🎤 Start Talking")
    if mic_button:
        st.write("Listening...")
        user_input = transcribe_audio("path_to_audio_file")
        st.text_area("Transcribed Input", user_input, height=100)
        return user_input
    return ""

def display_image(file):
    if file and file.type in ["image/jpeg", "image/png", "image/jpg"]:
        image = Image.open(file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

user_input = st.text_input("💬 Your message:")
user_input = voice_input_button() if user_input == "" else user_input

file_content = ""
if uploaded_file:
    file_bytes = uploaded_file.read()
    if uploaded_file.type == "application/pdf":
        file_content = file_bytes.decode("utf-8", errors="ignore")
    elif uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
        display_image(uploaded_file)
    elif uploaded_file.type == "text/plain":
        file_content = file_bytes.decode("utf-8", errors="ignore")

send_button = st.button("✉️ Send", use_container_width=True)

if st.button("🗨️ New Chat"):
    st.session_state.messages = []

# If message is sent
if send_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Construct prompt including system + file content
    full_messages = [{"role": "system", "content": "You are a knowledgeable tutor. Your goal is to explain complex topics in a simple and engaging way."}]
    if file_content:
        full_messages.append({"role": "user", "content": f"Here is some content:\n{file_content}"})
    full_messages.extend(st.session_state.messages)

    try:
        # Call Together API
        response = requests.post(
            TOGETHER_API_URL,
            headers={
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": full_messages,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )
        response.raise_for_status()
        bot_reply = response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        bot_reply = f"[Together API Error: {e}]"

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Show chat history
show_chat_history()

# Toggle dark mode
if st.button("🔄 Toggle Dark Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    toggle_dark_mode()

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import io
from PIL import Image
import speech_recognition as sr
import base64
import json

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("🤖 GPT-4o Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False  # default to light mode

# Handle theme toggle (Light/Dark mode)
def toggle_dark_mode():
    if st.session_state.dark_mode:
        st.write('<style>body { background-color: #333; color: white; }</style>', unsafe_allow_html=True)
    else:
        st.write('<style>body { background-color: #fff; color: black; }</style>', unsafe_allow_html=True)

toggle_dark_mode()

# File upload for text, image (jpg, png, jpeg), and audio (mp3, wav)
uploaded_file = st.file_uploader("📁 Upload a text file or image (jpg, png, jpeg, pdf)", type=["txt", "pdf", "jpg", "png", "jpeg"])

# Microphone button to start real-time voice input (Speech-to-Text)
def transcribe_audio(file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
    except Exception as e:
        return f"[Error transcribing audio: {e}]"

# Chat history panel
def show_chat_history():
    st.markdown("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Real-time voice input with Web Speech API (this should be implemented in frontend HTML/JS if Streamlit does not support real-time speech-to-text)
def voice_input_button():
    mic_button = st.button("🎤 Start Talking")
    if mic_button:
        st.write("Listening...")
        # For now, we just simulate the voice input in the text area:
        user_input = transcribe_audio("path_to_audio_file")
        st.text_area("Transcribed Input", user_input, height=100)
        return user_input
    return ""

# Display image if uploaded
def display_image(file):
    if file is not None and file.type in ["image/jpeg", "image/png", "image/jpg"]:
        image = Image.open(file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

# Handle text input
user_input = st.text_input("💬 Your message:")
user_input = voice_input_button() if user_input == "" else user_input  # Use voice input if no text

# File handling
file_content = ""
if uploaded_file:
    file_bytes = uploaded_file.read()
    if uploaded_file.type == "application/pdf":
        file_content = file_bytes.decode("utf-8", errors="ignore")
    elif uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
        display_image(uploaded_file)
    elif uploaded_file.type == "text/plain":
        file_content = file_bytes.decode("utf-8", errors="ignore")

# Send button for the message
send_button = st.button("✉️ Send", use_container_width=True)

# New chat button
if st.button("🗨️ New Chat"):
    st.session_state.messages = []

# Submit message to the chatbot
if send_button and user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Construct the prompt with the uploaded file content
    prompt = f"You are a helpful assistant. File content:\n{file_content}\n\nUser question:\n{user_input}"

    # Get GPT-4o response
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You're a helpful AI assistant."}] +
                     st.session_state.messages
        )
        bot_response = response.choices[0].message.content

    except Exception as e:
        bot_response = f"[OpenAI API error: {e}]"

    # Display bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Display chat history
show_chat_history()

# Dark mode toggle button
if st.button("🔄 Toggle Dark Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    toggle_dark_mode()


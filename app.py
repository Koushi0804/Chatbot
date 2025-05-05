import streamlit as st
import openai
from dotenv import load_dotenv
import os
import io
import base64

load_dotenv()  # Load variables from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


st.set_page_config(page_title="AI Chatbot", layout="wide")
st.title("🤖 GPT-4o Chatbot with File Upload & Voice Input")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# File upload (PDF, TXT, etc.)
uploaded_file = st.file_uploader("📁 Upload a text file", type=["txt", "pdf"])

# Audio upload
audio_file = st.file_uploader("🎤 Upload voice message (mp3, wav)", type=["mp3", "wav"])

# Convert audio to text using Whisper if provided
def transcribe_audio(file):
    try:
        transcript = openai.Audio.transcribe("whisper-1", file)
        return transcript["text"]
    except Exception as e:
        return f"[Error transcribing audio: {e}]"

# Handle user input from voice or text
if audio_file:
    st.success("Audio uploaded. Transcribing...")
    user_input = transcribe_audio(audio_file)
    st.text_area("Transcribed Input", user_input, height=100)
else:
    user_input = st.text_input("💬 Your message:")

# Submit message
if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare file content if uploaded
    file_content = ""
    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_content = file_bytes.decode("utf-8", errors="ignore")  # Simplified for TXT

    # Construct system prompt
    prompt = f"You are a helpful assistant. File content:\n{file_content}\n\nUser question:\n{user_input}"

    # Get GPT-4o response
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You're a helpful AI assistant."}] +
                     st.session_state.messages
        )
        bot_response = completion.choices[0].message.content
    except Exception as e:
        bot_response = f"[OpenAI API error: {e}]"

    # Display bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Show chat history
st.markdown("---")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

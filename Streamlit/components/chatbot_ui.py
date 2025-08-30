# components/chatbot_ui.py

import streamlit as st
from datetime import datetime
import time

# ==============================
# ⚙️ Helper: Format Timestamp
# ==============================
def format_timestamp(ts=None):
    """
    Returns the time in HH:MM format.
    If no timestamp is passed, uses current system time.
    """
    if ts is None:
        ts = datetime.now()
    return ts.strftime("%H:%M")


# ==============================
# 🎨 Global Chat CSS (scroll + blinking)
# ==============================
st.markdown("""
<style>
/* Scrollable chat container */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}

/* Blinking cursor */
.blinker { 
    animation: blink 1s step-start infinite; 
}
@keyframes blink { 
    50% { opacity: 0; } 
}
</style>
""", unsafe_allow_html=True)


# ==============================
# 🧑🏽‍🎓 Render User Message
# ==============================
def render_user_message(msg, timestamp=None):
    """
    Renders a chat bubble for the user message with timestamp.
    Args:
        msg (str): The user's text input
        timestamp (datetime, optional): Custom timestamp (default: current time)
    """
    ts = format_timestamp(timestamp)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #e0f7fa, #ccf2f4);
        padding: 12px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        font-family: 'Segoe UI', sans-serif;
    " class="chat-container">
        <strong>🧑🏽‍🎓 You:</strong> {msg}
        <div style="text-align: right; font-size: 0.75rem; color: #555;">{ts}</div>
    </div>
    """, unsafe_allow_html=True)


# ==============================
# 🤖 Render Bot Message with Typing Effect
# ==============================
def render_bot_message(msg, typing_delay=0.005, timestamp=None):
    """
    Renders a chat bubble for the bot response with typing animation.
    Args:
        msg (str): Bot's response text
        typing_delay (float): Delay between typing each chunk
        timestamp (datetime, optional): Custom timestamp (default: current time)
    """
    ts = format_timestamp(timestamp)
    placeholder = st.empty()  # Container for typing effect
    typed = ""                # Stores progressively typed characters
    
    # Split message into chunks to optimize rendering
    chunk_size = 2
    for i in range(0, len(msg), chunk_size):
        typed += msg[i:i+chunk_size]
        placeholder.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fff3e0, #ffe8c3);
            padding: 12px 15px;
            border-radius: 12px;
            margin-bottom: 12px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
            font-size: 1.05rem;
            font-family: 'Segoe UI', sans-serif;
        " class="chat-container">
            🤖 <strong>Smart Counsel AI:</strong> {typed}<span class="blinker">|</span>
            <div style="text-align: right; font-size: 0.75rem; color: #666;">{ts}</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(typing_delay)
    
    # Final render without blinking cursor
    placeholder.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #fff3e0, #ffe8c3);
        padding: 12px 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
        font-size: 1.05rem;
        font-family: 'Segoe UI', sans-serif;
    " class="chat-container">
        🤖 <strong>Smart Counsel AI:</strong> {typed}
        <div style="text-align: right; font-size: 0.75rem; color: #666;">{ts}</div>
    </div>
    """, unsafe_allow_html=True)

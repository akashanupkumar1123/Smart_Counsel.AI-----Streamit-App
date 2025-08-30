# components/ui_elements.py

import streamlit as st

# === Colored Title ===
def colored_title(text: str, emoji: str = "✨"):
    """
    Renders a section title with an emoji and colored text.
    Args:
        text (str): Title text
        emoji (str): Emoji to prefix the title (default: sparkle ✨)
    """
    st.markdown(f"### {emoji} <span style='color:#4A90E2'>{text}</span>", unsafe_allow_html=True)


# === Separator Line ===
def separator():
    """
    Renders a horizontal separator line (HR) with light gray border.
    Useful for dividing sections in the Streamlit app.
    """
    st.markdown("<hr style='border:1px solid #ccc;'>", unsafe_allow_html=True)


# === Highlighted Box ===
def highlight_box(message: str, color: str = "#f0f8ff"):
    """
    Renders a highlighted box with background color for emphasis.
    Args:
        message (str): The text/content to display inside the box
        color (str): Background color in HEX format (default: AliceBlue #f0f8ff)
    """
    st.markdown(f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 8px;">
        {message}
    </div>
    """, unsafe_allow_html=True)

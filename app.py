# app.py
import streamlit as st
from pathlib import Path
from utils.session_manager import init_session, new_chat
from utils.azure_api import ask_question

# --- Must be first Streamlit command ---
st.set_page_config(page_title="IntelliSwiftCare", page_icon="🤖")

# --- Load custom CSS ---
css_path = Path(__file__).parent / "static" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar branding ---
logo_path = Path(__file__).parent / "static" / "intelliswift_logo.png"
if logo_path.exists():
    st.sidebar.image(str(logo_path), width=140)
st.sidebar.markdown("## 🩺 IntelliSwift Care")
st.sidebar.markdown("**IntelliSwift Medical Research**")

# --- App Title ---
st.title("🩺IntelliSwift Healthcare Chatbot")
st.subheader("An initiative by IntelliSwift Medical Research")

# --- Initialize session state ---
init_session()

# --- New Chat button ---
col1, col2 = st.columns([8, 2])
with col1:
    st.write("Ask question from healthcare knowladgebase. Use `New Chat` to start a fresh conversation.")
with col2:
    if st.button("New Chat"):
        new_chat()

# --- Show current chat id ---
st.markdown(f"**Chat ID:** `{st.session_state.chat_id}`")
st.markdown("---")

# --- Chat window ---
chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-bubble'>You: {msg['content']}</div>", unsafe_allow_html=True)
        else:
            # text = msg.get("content", "")
            # sources = msg.get("sources", [])
            # if sources:
            #     text += "<br><br><small><b>Sources:</b><br>" + "<br>".join(sources) + "</small>"
            # st.markdown(f"<div class='assistant-bubble'>Assistant: {text}</div>", unsafe_allow_html=True)
                        # Show assistant bubble with answer
            st.markdown(f"<div class='assistant-bubble'>Assistant: {msg['content']}</div>", unsafe_allow_html=True)
                        # Show sources separately as clickable Markdown links
            sources = msg.get("sources", [])
            if sources:
                st.markdown("**Sources:**")
                for src in sources:
                    st.markdown(f"- {src}", unsafe_allow_html=True)

st.markdown("---")

# --- Question input ---
def submit_question():
    question = st.session_state.input_box
    if not question:
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})

    # Prepare history
    simple_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Ask backend
    resp = ask_question(st.session_state.user_id, st.session_state.chat_id, question, simple_history)

    # Handle response
    if resp.get("error"):
        ans = f"Error: {resp['error']}"
        sources = []
    else:
        ans = resp.get("answer", "No answer returned.")
        sources = resp.get("sources", [])

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": ans, "sources": sources})

    # Clear input
    st.session_state.input_box = ""

st.text_input("Ask a question:", key="input_box", on_change=submit_question)

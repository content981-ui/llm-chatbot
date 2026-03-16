import streamlit as st
import requests
import json
from typing import Generator

# Backend API URL
API_URL = "http://localhost:8000/api"


def fetch_sessions():
    """Fetch all chat sessions from the backend."""
    try:
        response = requests.get(f"{API_URL}/chats", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def create_session():
    """Create a new chat session."""
    try:
        response = requests.post(f"{API_URL}/chats", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def delete_session(session_id):
    """Delete a chat session."""
    try:
        response = requests.delete(f"{API_URL}/chats/{session_id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def fetch_messages(session_id):
    """Fetch all messages for a session."""
    try:
        response = requests.get(f"{API_URL}/chats/{session_id}/messages", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def send_message_stream(session_id, content) -> Generator[str, None, str]:
    """
    Send a message and yield tokens from streaming response.
    Returns the full response text when done.
    """
    try:
        response = requests.post(
            f"{API_URL}/chats/{session_id}/messages",
            json={"content": content},
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        if "token" in data:
                            token = data["token"]
                            full_response += token
                            yield token
                        elif data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        return full_response
    except requests.exceptions.RequestException as e:
        return ""


def update_session_title(session_id, title):
    """Update a session title."""
    try:
        response = requests.patch(
            f"{API_URL}/chats/{session_id}/title",
            json={"title": title},
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def check_ollama_status() -> bool:
    """Check if Ollama is running and responsive."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# Initialize session state
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False


# Page config
st.set_page_config(
    page_title="LLM Chatbot",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for dark theme and chat styling
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #1A1A1A;
    }
    .stSidebar .stButton > button {
        font-family: monospace;
    }
    
    /* Chat message styling */
    .chat-message-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }
    .chat-message-user > div {
        background-color: #1E3A5F;
        padding: 1rem;
        border-radius: 1rem;
        max-width: 70%;
    }
    .chat-message-assistant {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }
    .chat-message-assistant > div {
        background-color: #262730;
        padding: 1rem;
        border-radius: 1rem;
        max-width: 70%;
    }
    
    /* Hide default chat message styling */
    .stChatMessage {
        padding: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Two columns layout: sidebar + main
col_sidebar, col_main = st.columns([1, 3], gap="medium")

with col_sidebar:
    st.markdown("### 💬 Chats")

    # New Chat button
    if st.button("＋ New Chat", use_container_width=True, key="new_chat_btn"):
        new_session = create_session()
        if new_session:
            st.session_state.current_session_id = new_session["id"]
            st.session_state.messages = []
            st.session_state.sessions = fetch_sessions()
            st.rerun()

    st.divider()

    # Refresh sessions
    st.session_state.sessions = fetch_sessions()

    # Chat list
    if not st.session_state.sessions:
        st.info("No chats yet. Start a new one!")
    else:
        for session in st.session_state.sessions:
            session_id = session["id"]
            title = session["title"]

            # Truncate title if too long
            display_title = title[:28] + "..." if len(title) > 28 else title

            # Create two columns for chat item and delete button
            item_col, delete_col = st.columns([4, 1])

            with item_col:
                if st.button(
                    display_title,
                    key=f"chat_{session_id}",
                    use_container_width=True,
                    type="primary" if session_id == st.session_state.current_session_id else "secondary"
                ):
                    st.session_state.current_session_id = session_id
                    st.session_state.messages = fetch_messages(session_id)
                    st.rerun()

            with delete_col:
                if st.button("🗑️", key=f"delete_{session_id}", help="Delete chat"):
                    delete_session(session_id)
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                    st.session_state.sessions = fetch_sessions()
                    st.rerun()

with col_main:
    # Check Ollama status
    ollama_running = check_ollama_status()
    
    if not ollama_running:
        st.error("⚠️ **Local AI model is offline.** Please start Ollama with `ollama serve`")
    
    if st.session_state.current_session_id is None:
        # No session selected - show welcome message
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 60vh;">
                <h2 style="color: #888;">Select a chat or start a new one</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Load messages if empty (e.g., after session selection)
        if not st.session_state.messages:
            st.session_state.messages = fetch_messages(st.session_state.current_session_id)

        # Display chat messages with custom styling
        messages_container = st.container()
        with messages_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-message-user"><div>{msg["content"]}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-message-assistant"><div>{msg["content"]}</div></div>',
                        unsafe_allow_html=True
                    )

        # Chat input at the bottom
        if prompt := st.chat_input("Type your message..."):
            if not ollama_running:
                st.error("⚠️ Local AI model is offline. Please start Ollama with `ollama serve`")
            else:
                # Check if this is the first message (for auto-title)
                is_first_message = len(st.session_state.messages) == 0
                original_prompt = prompt

                # Append user message to session state and display
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                # Send message and stream response
                with st.chat_message("assistant"):
                    try:
                        # Use st.write_stream for proper streaming
                        def token_generator():
                            for token in send_message_stream(st.session_state.current_session_id, prompt):
                                yield token

                        full_response = st.write_stream(token_generator)
                    except Exception as e:
                        st.write(f"⚠️ Error: {str(e)}")
                        full_response = ""

                    # Add assistant response to session state
                    if full_response:
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                    # Auto-rename chat if this is the first message
                    if is_first_message and original_prompt:
                        auto_title = original_prompt[:40] + "..." if len(original_prompt) > 40 else original_prompt
                        update_session_title(st.session_state.current_session_id, auto_title)
                        st.session_state.sessions = fetch_sessions()

                st.rerun()

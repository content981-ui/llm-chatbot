import streamlit as st
import requests
import json

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


def send_message(session_id, content):
    """Send a message and get streaming response."""
    try:
        response = requests.post(
            f"{API_URL}/chats/{session_id}/messages",
            json={"content": content},
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return None


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


# Initialize session state
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = []


# Page config
st.set_page_config(
    page_title="LLM Chatbot",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for better layout
st.markdown("""
<style>
    .stSidebar {
        background-color: #1A1A1A;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Two columns layout: sidebar + main
col_sidebar, col_main = st.columns([1, 3])

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
    if st.session_state.current_session_id is None:
        # No session selected - show welcome message
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 80vh;">
                <h2 style="color: #888;">Select a chat or start a new one</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Load messages if empty (e.g., after session selection)
        if not st.session_state.messages:
            st.session_state.messages = fetch_messages(st.session_state.current_session_id)
        
        # Display chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Add spacer to push chat input to the bottom
        st.space()

        # Chat input
        if prompt := st.chat_input("Type your message..."):
            # Append user message to session state and display
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Send message and stream response
            with st.chat_message("assistant"):
                response = send_message(st.session_state.current_session_id, prompt)
                
                if response is None:
                    st.write("⚠️ Failed to connect to backend. Make sure it's running.")
                else:
                    # Stream the response
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
                                        # Write token to stream
                                        st.markdown(token, unsafe_allow_html=True)
                                    elif data.get("done"):
                                        break
                                except json.JSONDecodeError:
                                    continue
                    
                    # Add assistant response to session state
                    if full_response:
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Auto-rename chat if this is the first message
                    if len(st.session_state.messages) == 2:  # user + assistant
                        auto_title = prompt[:40] + "..." if len(prompt) > 40 else prompt
                        update_session_title(st.session_state.current_session_id, auto_title)
                        st.session_state.sessions = fetch_sessions()
            
            st.rerun()

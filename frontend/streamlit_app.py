# ui/streamlit_app.py

import streamlit as st
import requests, os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# ==========================================================
# CONFIG
# ==========================================================

API_BASE_URL = f"{os.getenv('API_BASE_URL', 'http://localhost:8000')}/api/v1"

st.set_page_config(
    page_title="Document Parser AI",
    page_icon="📄",
    layout="wide",
)

# ==========================================================
# SESSION STATE INIT
# ==========================================================

DEFAULT_STATES = {
    "current_page": "Dashboard",
    "selected_document": None,
    "api_error": None,
    "last_refresh": datetime.now().strftime("%B %d, %Y %I:%M %p"),
    "db_initialized": True,
}

for key, value in DEFAULT_STATES.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# SAFE HELPERS
# ==========================================================

def ensure_dict(data):
    return data if isinstance(data, dict) else {}

def ensure_list(data):
    return data if isinstance(data, list) else []

def safe_str(value):
    return str(value) if value is not None else ""

def format_date(date_value: Optional[object]) -> str:
    if not date_value:
        return "N/A"

    try:
        # Convert to datetime
        if isinstance(date_value, datetime):
            dt = date_value
        else:
            dt = datetime.fromisoformat(str(date_value).replace("Z", "+00:00"))

        # If datetime is naive, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        # Convert to IST
        IST = ZoneInfo("Asia/Kolkata")
        dt_ist = dt.astimezone(IST)

        # Indian readable format in IST
        return dt_ist.strftime("%d %B %Y, %I:%M %p")

    except Exception:
        return "Invalid Date"

def format_file_size(size_bytes: Optional[int]) -> str:
    if not size_bytes:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_status_badge(status: str):
    status = safe_str(status).lower()
    color_map = {
        "pending": "orange",
        "processing": "blue",
        "completed": "green",
        "failed": "red",
    }
    color = color_map.get(status, "gray")
    return f"<span style='color:{color};font-weight:bold'>{status.upper()}</span>"


# ==========================================================
# API CLIENT (Industrial Safe)
# ==========================================================

def make_api_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    param = "&".join([f"{key}={value}" for key, value in kwargs.get("data", {}).items()])
    url = f"{API_BASE_URL}{endpoint}"
    if param and method.upper() == "GET":
        url += f"?{param}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)

        if response.status_code in [200, 201]:
            try:
                return {"success": True, "data": response.json()}
            except:
                return {"success": True, "data": {}}

        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code,
        }

    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Backend server not reachable"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==========================================================
# HEALTH CHECK (CACHED)
# ==========================================================

@st.cache_data(ttl=10)
def check_api():
    return make_api_request("GET", "/health")

api_status = check_api()

if not api_status["success"]:
    st.error("🚨 Backend API not running. Please start FastAPI server.")
    st.stop()


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

PAGE_MAP = {
    "📊 Dashboard": "Dashboard",
    "📤 Upload Document": "Upload",
    "📋 Document List": "Document List",
    "🔍 Chat Documents": "Chat"
}

selected = st.sidebar.radio("Navigation", list(PAGE_MAP.keys()))
st.session_state.current_page = PAGE_MAP[selected]

st.sidebar.caption(f"Last Refresh: {st.session_state.last_refresh}")

if st.sidebar.button("🔄 Refresh"):
    st.session_state.last_refresh = datetime.now().strftime("%B %d, %Y %I:%M %p")
    st.cache_data.clear()
    st.rerun()

page = st.session_state.current_page

# ==========================================================
# DASHBOARD
# ==========================================================

if page == "Dashboard":
    st.title("📊 Dashboard")

    response = make_api_request("GET", "/documents/stats/")
    if not response["success"]:
        st.error(response["error"])
        st.stop()

    stats = ensure_dict(response.get("data",{}))

    total = stats.get("total", 0)
    completed = stats.get("completed", 0)
    failed = stats.get("failed", 0)
    pending = stats.get("pending", 0)
    processing = stats.get("processing", 0)

    if total == 0:
        st.info("No documents uploaded yet.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("Completed", completed)
    col3.metric("Failed", failed)
    col4.metric("Pending", pending + processing)

    success_rate = (completed / total * 100) if total > 0 else 0
    st.metric("Success Rate", f"{success_rate:.2f}%")

    chart_df = pd.DataFrame({
        "Status": ["Pending", "Processing", "Completed", "Failed"],
        "Count": [pending, processing, completed, failed]
    })

    st.bar_chart(chart_df.set_index("Status"))

# ==========================================================
# UPLOAD
# ==========================================================

elif page == "Upload":
    st.title("📤 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "txt", "md", "docx"]
    )

    if not uploaded_file:
        st.info("Select a document to upload.")
        st.stop()

    st.write("Filename:", uploaded_file.name)
    st.write("Size:", format_file_size(uploaded_file.size))

    if uploaded_file.type and uploaded_file.type.startswith("image"):
        try:
            img = Image.open(uploaded_file)
            st.image(img)
        except:
            st.warning("Cannot preview image")

    if st.button("Upload & Process"):
        with st.spinner("Uploading..."):
            uploaded_file.seek(0)
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }
            response = make_api_request("POST", "/documents/upload", files=files)

        if response["success"]:
            doc = ensure_dict(response.get("data"))
            st.success("Upload successful!")
            st.json(doc)
        else:
            st.error(response["error"])

# ==========================================================
# DOCUMENT LIST
# ==========================================================

elif page == "Document List":
    st.title("📋 Document List")

    # -----------------------------
    # Pagination State
    # -----------------------------
    if "doc_page" not in st.session_state:
        st.session_state.doc_page = 1

    PAGE_SIZE = 10

    current_page = st.session_state.doc_page

    # -----------------------------
    # API Call
    # -----------------------------
    response = make_api_request(
        "GET",
        "/documents/",
        data={
            "page": current_page,
            "page_size": PAGE_SIZE
        }
    )

    if not response["success"]:
        st.error(response["error"])
        st.stop()

    response_data = ensure_dict(response.get("data"))
    documents = ensure_list(response_data.get("data"))

    pagination = ensure_dict(response_data.get("pagination"))

    total_pages = pagination.get("total_pages", 1)
    total_records = pagination.get("total_records", 0)

    if not documents:
        st.info("No documents found.")
        st.stop()

    st.caption(f"📊 Page {current_page} of {total_pages} | Total Records: {total_records}")

    st.divider()

    # -----------------------------
    # Document List Rendering
    # -----------------------------
    for doc in documents:
        doc = ensure_dict(doc)

        doc_id = safe_str(doc.get("id"))
        short_id = doc_id[:8] + "..." if len(doc_id) > 8 else doc_id

        with st.container():
            cols = st.columns([1, 3, 2, 2])

            cols[0].write(short_id)
            cols[1].write(doc.get("filename", "N/A"))
            cols[2].markdown(
                get_status_badge(doc.get("status")),
                unsafe_allow_html=True
            )
            cols[3].write(format_date(doc.get("created_at")))

            st.divider()

    # -----------------------------
    # Pagination Controls Bottom
    # -----------------------------
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if current_page > 1:
            if st.button("⬅️ Previous Page"):
                st.session_state.doc_page -= 1
                st.rerun()

    with col2:
        st.write(f"Page {current_page} / {total_pages}")

    with col3:
        if current_page < total_pages:
            if st.button("Next Page ➡️"):
                st.session_state.doc_page += 1
                st.rerun()

# ==========================================================
# Chat
# ==========================================================

elif page == "Chat":
    st.title("💬 Chat with Documents")
    
    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for chat controls only
    with st.sidebar:
        st.subheader("Chat Settings")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.divider()
        
        # Model info
        st.info("🤖 Using Gemini AI model")
        
        st.divider()
        
        # Simple chat stats
        total_messages = len(st.session_state.chat_history)
        if total_messages > 0:
            user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
            st.metric("Total Messages", total_messages)
            st.metric("Your Questions", user_messages)
            st.metric("AI Responses", assistant_messages)
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"🕐 {message['timestamp']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {timestamp}")
        
        # Display assistant response with spinner
        with st.chat_message("assistant"):
            with st.spinner("Generating answer..."):
                try:
                    # Make API call to your /query/ endpoint
                    # IMPORTANT: Use 'json' parameter, not 'data'
                    response = make_api_request(
                        "POST", 
                        "/documents/query/", 
                        json={"question": prompt},  # This sends as proper JSON
                        headers={"Content-Type": "application/json"}
                    )
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if response["success"]:
                        # Extract data from response
                        data = response["data"]
                        answer = data.get("answer", "Sorry, I couldn't generate a response.")
                        
                        # Display answer
                        st.markdown(answer)
                        st.caption(f"🕐 {timestamp}")
                        
                        # Add assistant message to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "timestamp": timestamp
                        })
                    else:
                        error_msg = response.get("error", "Unknown error occurred")
                        st.error(f"Error: {error_msg}")
                        
                        # Add error as assistant message
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"❌ Error: {error_msg}",
                            "timestamp": timestamp
                        })
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"❌ Error: {str(e)}",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
    
    # Export chat button
    if st.session_state.chat_history:
        st.divider()
        if st.button("📥 Export Chat History", use_container_width=True):
            chat_text = ""
            for msg in st.session_state.chat_history:
                role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
                timestamp = msg.get("timestamp", "")
                chat_text += f"{role} [{timestamp}]:\n{msg['content']}\n\n"
            
            st.download_button(
                label="Download as Text File",
                data=chat_text,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    # Welcome message for empty chat
    if not st.session_state.chat_history:
        st.info("👋 Welcome! Ask me anything about your documents.")

# ==========================================================
# FOOTER
# ==========================================================

st.divider()
st.caption("Document Parser AI | Built with Streamlit & FastAPI")
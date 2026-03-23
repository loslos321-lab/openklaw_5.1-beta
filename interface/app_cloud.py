"""
KimiClaw Master Coder - Cloud Version
Standalone Web Interface for Streamlit Cloud
"""

import streamlit as st
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="KimiClaw Interface",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Determine base directory (works on Windows and Linux)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Simple JSON-based database for cloud
class CloudDatabase:
    def __init__(self):
        self.tasks_file = DATA_DIR / "tasks.json"
        self.logs_file = DATA_DIR / "logs.json"
        self.economy_file = DATA_DIR / "economy.json"
        self.init_data()
    
    def init_data(self):
        if not self.tasks_file.exists():
            default_tasks = [
                {
                    "task_id": "coding-task-001",
                    "sector": "Technology",
                    "occupation": "Software Developer",
                    "title": "CSV Statistics Calculator",
                    "description": "Create a Python function that reads CSV and calculates statistics",
                    "prompt": "Create a Python function that reads a CSV file and calculates statistics (mean, median, mode) for numeric columns. Include error handling and documentation.",
                    "estimated_hours": 2,
                    "max_payment": 50.0,
                    "status": "pending"
                },
                {
                    "task_id": "coding-task-002",
                    "sector": "Technology",
                    "occupation": "Web Developer",
                    "title": "FastAPI Todo API",
                    "description": "Build a REST API for Todo items",
                    "prompt": "Build a simple REST API using FastAPI with CRUD operations for a 'Todo' item.",
                    "estimated_hours": 3,
                    "max_payment": 75.0,
                    "status": "pending"
                }
            ]
            self._save_json(self.tasks_file, default_tasks)
        
        if not self.economy_file.exists():
            self._save_json(self.economy_file, {"balance": 100.0, "transactions": []})
        
        if not self.logs_file.exists():
            self._save_json(self.logs_file, [])
    
    def _load_json(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_tasks(self):
        return self._load_json(self.tasks_file)
    
    def get_pending_tasks(self):
        tasks = self._load_json(self.tasks_file)
        return [t for t in tasks if t.get('status') == 'pending']
    
    def update_task_status(self, task_id, status):
        tasks = self._load_json(self.tasks_file)
        for task in tasks:
            if task['task_id'] == task_id:
                task['status'] = status
                break
        self._save_json(self.tasks_file, tasks)
    
    def add_task(self, task):
        tasks = self._load_json(self.tasks_file)
        tasks.append(task)
        self._save_json(self.tasks_file, tasks)
    
    def get_balance(self):
        data = self._load_json(self.economy_file)
        return data.get('balance', 100.0)
    
    def add_log(self, run_id, level, message):
        logs = self._load_json(self.logs_file)
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id,
            "level": level,
            "message": message
        })
        self._save_json(self.logs_file, logs[-100:])  # Keep last 100
    
    def get_logs(self, limit=100):
        logs = self._load_json(self.logs_file)
        return logs[-limit:]

# Initialize database
db = CloudDatabase()

# Session state
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'current_run_id' not in st.session_state:
    st.session_state.current_run_id = None

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .status-running { color: #00cc00; font-weight: bold; }
    .status-stopped { color: #cc0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🦞 KimiClaw")
    st.caption("Master Coder Interface")
    st.divider()
    
    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "▶️ Agent",
        "📋 Tasks", 
        "💰 Economy",
        "⚙️ Settings"
    ])

# Main content
st.markdown("<h1 style='color: #1f77b4;'>KimiClaw Master Coder</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666;'>Cloud Version - AI Code Agent</p>", unsafe_allow_html=True)

# Load secrets
def get_api_key():
    """Get API key from Streamlit secrets or return empty"""
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except:
        return ""

# Dashboard
if "Dashboard" in page:
    st.header("🏠 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        balance = db.get_balance()
        st.metric("💰 Balance", f"${balance:.2f}")
    
    with col2:
        pending = len(db.get_pending_tasks())
        st.metric("📋 Pending Tasks", pending)
    
    with col3:
        status = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
        st.metric("📡 Status", status)
    
    with col4:
        api_key = get_api_key()
        has_key = "✅" if api_key else "❌"
        st.metric("🔑 API Key", has_key)
    
    st.divider()
    
    if not api_key:
        st.error("⚠️ No API Key configured!")
        st.info("Go to ⚙️ Settings and add your API Key in Streamlit Secrets")
    
    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Agent", type="primary", use_container_width=True):
            st.session_state.nav_override = "▶️ Agent"
            st.rerun()
    with col2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.nav_override = "⚙️ Settings"
            st.rerun()

# Agent Control
elif "Agent" in page:
    st.header("▶️ Agent Control")
    
    api_key = get_api_key()
    
    if not api_key:
        st.error("⚠️ No API Key configured!")
        st.info("Add your API Key in Streamlit Cloud: Settings > Secrets")
        st.code("""
[secrets]
OPENAI_API_KEY = "sk-your-key-here"
OPENAI_API_BASE = "https://api.moonshot.cn/v1"
        """, language="toml")
    else:
        st.success(f"✅ API Key configured: {api_key[:15]}...")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Start Agent")
        mode = st.selectbox("Mode", ["work", "interactive", "sandbox"], 
                           format_func=lambda x: {"work": "💼 Work Mode", "interactive": "💬 Interactive", "sandbox": "🏖️ Sandbox"}[x])
        
        if st.button("▶️ START AGENT", type="primary", use_container_width=True):
            if not api_key:
                st.error("Please configure API Key first!")
            else:
                st.session_state.is_running = True
                run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                st.session_state.current_run_id = run_id
                db.add_log(run_id, "INFO", f"Agent started in {mode} mode")
                st.success(f"Agent started! Run ID: {run_id}")
                st.rerun()
    
    with col2:
        st.subheader("Status")
        if st.session_state.is_running:
            st.markdown("<span style='color: #00cc00; font-weight: bold;'>● RUNNING</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #cc0000; font-weight: bold;'>● STOPPED</span>", unsafe_allow_html=True)
        
        if st.button("⏹️ STOP", use_container_width=True, disabled=not st.session_state.is_running):
            st.session_state.is_running = False
            st.success("Agent stopped!")
            st.rerun()
    
    st.divider()
    st.subheader("Live Logs")
    
    if st.session_state.current_run_id:
        logs = db.get_logs(limit=20)
        for log in logs:
            st.text(f"[{log.get('timestamp', '')}] {log.get('level', 'INFO')}: {log.get('message', '')}")
    else:
        st.info("No logs available. Start the agent first.")

# Tasks
elif "Tasks" in page:
    st.header("📋 Task Management")
    
    tasks = db.get_all_tasks()
    st.write(f"Total tasks: {len(tasks)}")
    
    # Add new task
    with st.expander("➕ Add New Task"):
        with st.form("new_task"):
            task_id = st.text_input("Task ID", value=f"task-{int(time.time())}")
            title = st.text_input("Title")
            description = st.text_area("Description")
            prompt = st.text_area("Prompt", height=100)
            
            if st.form_submit_button("Add Task"):
                db.add_task({
                    "task_id": task_id,
                    "sector": "Technology",
                    "occupation": "Developer",
                    "title": title,
                    "description": description,
                    "prompt": prompt,
                    "estimated_hours": 2,
                    "max_payment": 50.0,
                    "status": "pending"
                })
                st.success("Task added!")
                st.rerun()
    
    # Task list
    for task in tasks:
        with st.expander(f"{task.get('title', 'Untitled')} ({task.get('task_id')})"):
            st.write(f"**Description:** {task.get('description', 'N/A')}")
            st.write(f"**Status:** {task.get('status', 'pending')}")
            st.write(f"**Max Payment:** ${task.get('max_payment', 0)}")
            if st.button("Mark Complete", key=f"complete_{task.get('task_id')}"):
                db.update_task_status(task.get('task_id'), 'completed')
                st.rerun()

# Economy
elif "Economy" in page:
    st.header("💰 Economy Dashboard")
    
    balance = db.get_balance()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"${balance:.2f}")
    with col2:
        st.metric("Initial Balance", "$100.00")
    with col3:
        profit = balance - 100.0
        st.metric("Profit/Loss", f"${profit:.2f}")

# Settings
elif "Settings" in page:
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    st.info("In Streamlit Cloud, add your secrets in Settings > Secrets:")
    
    st.code("""
[secrets]
OPENAI_API_KEY = "sk-your-key-here"
OPENAI_API_BASE = "https://api.moonshot.cn/v1"
EVALUATION_API_KEY = "sk-your-key-here"
EVALUATION_API_BASE = "https://api.moonshot.cn/v1"
    """, language="toml")
    
    st.subheader("Current Status")
    api_key = get_api_key()
    if api_key:
        st.success(f"✅ API Key: {api_key[:20]}...")
    else:
        st.error("❌ No API Key configured")
    
    st.subheader("Help")
    st.info("""
    **Getting API Keys:**
    
    1. **SiliconFlow** (14M free tokens)
       - https://cloud.siliconflow.cn/
    
    2. **Kimi (Moonshot AI)**
       - https://platform.moonshot.cn/
    """)

# Footer
st.divider()
st.caption("Made with ❤️ by KimiClaw | Cloud Version")

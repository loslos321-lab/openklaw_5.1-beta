"""
KimiClaw Master Coder - GitHub-Style Interface
Professional Web IDE for AI Code Agent
"""

import streamlit as st
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Page config - Dark theme like GitHub
st.set_page_config(
    page_title="KimiClaw | AI Code Agent",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# GitHub Dark Theme CSS
st.markdown("""
<style>
    /* Global Dark Theme */
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Header */
    .github-header {
        background: linear-gradient(90deg, #161b22 0%, #21262d 100%);
        border-bottom: 1px solid #30363d;
        padding: 16px 24px;
        margin: -1rem -1rem 0 -1rem;
    }
    
    /* Code Editor Style */
    .code-editor {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-family: 'SF Mono', Monaco, Consolas, monospace;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* File Browser */
    .file-tree {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
        min-height: 100vh;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-bottom: 1px solid #30363d;
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8b949e;
        border: none;
        padding: 12px 16px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        color: #c9d1d9 !important;
        border-bottom: 2px solid #f78166 !important;
    }
    
    /* Buttons - GitHub Style */
    .stButton > button {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(240,246,252,0.1);
        border-radius: 6px;
        padding: 6px 16px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
        border-color: rgba(240,246,252,0.1);
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #30363d;
    }
    
    /* Status Indicators */
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .status-idle { background-color: #8b949e; }
    .status-running { background-color: #3fb950; animation: pulse 2s infinite; }
    .status-error { background-color: #f85149; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Cards */
    .gh-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .gh-card-header {
        border-bottom: 1px solid #21262d;
        padding-bottom: 12px;
        margin-bottom: 12px;
        font-weight: 600;
        color: #c9d1d9;
    }
    
    /* Terminal/Console */
    .terminal {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        font-family: 'SF Mono', Monaco, Consolas, monospace;
        font-size: 13px;
        color: #c9d1d9;
        min-height: 300px;
        overflow-y: auto;
    }
    
    .terminal-line {
        margin: 4px 0;
    }
    
    .terminal-prompt {
        color: #7ee787;
    }
    
    .terminal-error {
        color: #f85149;
    }
    
    .terminal-success {
        color: #3fb950;
    }
    
    /* Metrics */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #c9d1d9;
    }
    
    .metric-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #c9d1d9;
        border-radius: 6px;
    }
    
    .stSelectbox > div > div {
        background-color: #21262d;
        border: 1px solid #30363d;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
    }
    
    /* Expander */
    .streamlit-expander {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    
    /* Toast notifications */
    .stToast {
        background-color: #161b22;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

# GitHub-Style Header
st.markdown("""
<div class="github-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 24px;">🦞</span>
            <span style="font-size: 18px; font-weight: 600; color: #c9d1d9;">KimiClaw</span>
            <span style="color: #8b949e; font-size: 14px;">AI Code Agent</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-size: 13px; color: #8b949e;">v2.0.0-beta</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Bar
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])

with col1:
    if st.button("📊 Dashboard", use_container_width=True, 
                 type="primary" if st.session_state.page == 'dashboard' else "secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()

with col2:
    if st.button("📝 Editor", use_container_width=True,
                 type="primary" if st.session_state.page == 'editor' else "secondary"):
        st.session_state.page = 'editor'
        st.rerun()

with col3:
    if st.button("📋 Tasks", use_container_width=True,
                 type="primary" if st.session_state.page == 'tasks' else "secondary"):
        st.session_state.page = 'tasks'
        st.rerun()

with col4:
    if st.button("▶️ Run", use_container_width=True,
                 type="primary" if st.session_state.page == 'run' else "secondary"):
        st.session_state.page = 'run'
        st.rerun()

with col5:
    if st.button("⚙️ Settings", use_container_width=True,
                 type="primary" if st.session_state.page == 'settings' else "secondary"):
        st.session_state.page = 'settings'
        st.rerun()

with col6:
    # Status indicator
    status_color = "status-running" if st.session_state.is_running else "status-idle"
    status_text = "Running" if st.session_state.is_running else "Idle"
    st.markdown(f"""
    <div style="text-align: right; padding-top: 8px;">
        <span class="status-dot {status_color}"></span>
        <span style="color: #8b949e; font-size: 13px; margin-left: 6px;">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 0; border-color: #21262d;'>", unsafe_allow_html=True)

# DATABASE (Cloud-compatible)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class CloudDB:
    def __init__(self):
        self.tasks_file = DATA_DIR / "tasks.json"
        self.init_data()
    
    def init_data(self):
        if not self.tasks_file.exists():
            default_tasks = [
                {
                    "id": "task-001",
                    "title": "Hello World Function",
                    "description": "Create a simple greeting function",
                    "code": "def greet(name):\n    return f'Hello, {name}!'",
                    "language": "python",
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "task-002", 
                    "title": "CSV Reader",
                    "description": "Read and process CSV files",
                    "code": "import pandas as pd\n\ndef read_csv(filepath):\n    return pd.read_csv(filepath)",
                    "language": "python",
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
            ]
            with open(self.tasks_file, 'w') as f:
                json.dump(default_tasks, f)
    
    def get_tasks(self):
        with open(self.tasks_file, 'r') as f:
            return json.load(f)

db = CloudDB()

# PAGES

# DASHBOARD
if st.session_state.page == 'dashboard':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">$100.00</div>
            <div class="metric-label">Balance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tasks = db.get_tasks()
        pending = len([t for t in tasks if t['status'] == 'pending'])
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{pending}</div>
            <div class="metric-label">Pending Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">12</div>
            <div class="metric-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">98.5%</div>
            <div class="metric-label">Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recent Activity
        st.markdown("""
        <div class="gh-card">
            <div class="gh-card-header">Recent Activity</div>
        </div>
        """, unsafe_allow_html=True)
        
        activities = [
            ("🟢", "Task completed: CSV Reader", "2 minutes ago"),
            ("📝", "New task created: API Test", "15 minutes ago"),
            ("🤖", "Agent started: Work Mode", "1 hour ago"),
        ]
        
        for icon, text, time in activities:
            st.markdown(f"""
            <div style="padding: 12px; border-bottom: 1px solid #21262d;">
                <span style="margin-right: 8px;">{icon}</span>
                <span style="color: #c9d1d9;">{text}</span>
                <span style="color: #8b949e; float: right; font-size: 12px;">{time}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Quick Actions
        st.markdown("""
        <div class="gh-card">
            <div class="gh-card-header">Quick Actions</div>
            <div style="display: flex; flex-direction: column; gap: 8px;">
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ New Task", use_container_width=True):
            st.session_state.page = 'tasks'
            st.rerun()
        
        if st.button("▶️ Start Agent", use_container_width=True):
            st.session_state.page = 'run'
            st.rerun()

# EDITOR
elif st.session_state.page == 'editor':
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # File Tree
        st.markdown("""
        <div class="gh-card" style="min-height: 500px;">
            <div class="gh-card-header">Files</div>
        </div>
        """, unsafe_allow_html=True)
        
        files = ["main.py", "utils.py", "test.py", "README.md"]
        for file in files:
            icon = "📄" if file.endswith('.md') else "🐍"
            st.markdown(f"""
            <div style="padding: 8px; cursor: pointer; border-radius: 4px;" 
                 onmouseover="this.style.backgroundColor='#21262d'" 
                 onmouseout="this.style.backgroundColor='transparent'">
                <span>{icon}</span>
                <span style="color: #c9d1d9; margin-left: 8px; font-size: 14px;">{file}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Code Editor
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="color: #c9d1d9; font-weight: 500;">main.py</span>
            <span style="color: #8b949e; font-size: 12px;">Python</span>
        </div>
        """, unsafe_allow_html=True)
        
        code = st.text_area("", value='''def main():
    """Main function for the agent."""
    print("Starting KimiClaw Agent...")
    
    # Initialize
    balance = 100.0
    tasks = load_tasks()
    
    # Process tasks
    for task in tasks:
        result = process_task(task)
        if result.success:
            balance += result.payment
            
    return balance

if __name__ == "__main__":
    main()
''', height=400, label_visibility="collapsed")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            st.button("💾 Save", use_container_width=True)
        with col2:
            st.button("▶️ Run", use_container_width=True)

# TASKS
elif st.session_state.page == 'tasks':
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("📋 Tasks")
    
    with col2:
        if st.button("➕ New Task", use_container_width=True):
            st.session_state.show_new_task = True
    
    # Task List
    tasks = db.get_tasks()
    
    for task in tasks:
        with st.expander(f"{task['title']} ({task['id']})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Description:** {task['description']}")
                st.markdown(f"**Status:** {task['status']}")
                st.markdown(f"**Created:** {task['created_at'][:10]}")
            with col2:
                if task['status'] == 'pending':
                    if st.button("▶️ Run", key=f"run_{task['id']}"):
                        st.session_state.current_task = task
                        st.session_state.page = 'run'
                        st.rerun()

# RUN
elif st.session_state.page == 'run':
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("▶️ Agent Execution")
    
    with col2:
        if st.session_state.is_running:
            if st.button("⏹️ Stop Agent", use_container_width=True):
                st.session_state.is_running = False
                st.success("Agent stopped!")
                st.rerun()
        else:
            if st.button("▶️ Start Agent", use_container_width=True):
                st.session_state.is_running = True
                st.rerun()
    
    # Terminal Output
    st.markdown("""
    <div style="margin-top: 16px;">
        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px 6px 0 0; 
                    padding: 8px 16px; display: flex; align-items: center; gap: 8px;">
            <span style="color: #8b949e; font-size: 12px;">TERMINAL</span>
            <span style="color: #3fb950; font-size: 12px;">●</span>
        </div>
        <div class="terminal">
    """, unsafe_allow_html=True)
    
    if st.session_state.is_running:
        logs = [
            ("$", "kimi-agent start --mode=work", "prompt"),
            ("", "Initializing KimiClaw Agent v2.0...", "info"),
            ("", "✓ Database connected", "success"),
            ("", "✓ API configured", "success"),
            ("", "Loading tasks...", "info"),
            ("", "Found 2 pending tasks", "info"),
            ("", "Processing task: Hello World Function", "info"),
            ("", "Generating code...", "info"),
        ]
        for prefix, msg, msg_type in logs:
            if msg_type == "prompt":
                st.markdown(f'<div class="terminal-line"><span class="terminal-prompt">{prefix}</span> {msg}</div>', unsafe_allow_html=True)
            elif msg_type == "success":
                st.markdown(f'<div class="terminal-line terminal-success">{msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="terminal-line">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-line" style="color: #8b949e;">Agent is idle. Click "Start Agent" to begin.</div>', unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# SETTINGS
elif st.session_state.page == 'settings':
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    st.header("⚙️ Settings")
    
    tabs = st.tabs(["API Keys", "Agent Config", "Theme"])
    
    with tabs[0]:
        st.subheader("API Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("OpenAI/Kimi API Key", type="password", 
                                   value="sk-...", help="Your API key from Kimi or SiliconFlow")
        with col2:
            api_base = st.text_input("API Base URL", 
                                    value="https://api.moonshot.cn/v1")
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")
    
    with tabs[1]:
        st.subheader("Agent Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Initial Balance ($)", value=100.0, step=10.0)
            st.number_input("Max Steps", value=20, step=1)
        with col2:
            st.selectbox("Model", ["kimi-k2-0725", "gpt-4o", "Qwen2.5"])
            st.selectbox("Mode", ["work", "interactive", "sandbox"])
    
    with tabs[2]:
        st.subheader("Appearance")
        st.selectbox("Theme", ["Dark (GitHub)", "Light", "System"])
        st.checkbox("Show line numbers in editor", value=True)

# Footer
st.markdown("<div style='padding: 32px 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid #21262d; padding: 16px 0; text-align: center; color: #8b949e; font-size: 12px;">
    🦞 KimiClaw v2.0.0-beta | Made with ❤️ | 
    <a href="https://github.com/loslos321-lab/openklaw_5.1-beta" style="color: #58a6ff;">GitHub</a>
</div>
""", unsafe_allow_html=True)

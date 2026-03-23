"""
KimiClaw Master Coder - Web Interface mit SQLite
"""

import streamlit as st
import sys
import os
import json
import time
import subprocess
import threading
import queue
from pathlib import Path
from datetime import datetime

# Set up paths for ClawWork
BASE_DIR = Path("c:/Users/Student/kimiclaw")
CLAWWORK_DIR = Path("c:/Users/Student/ClawWork")

# Add to Python path
sys.path.insert(0, str(CLAWWORK_DIR))
sys.path.insert(0, str(CLAWWORK_DIR / "livebench"))
sys.path.insert(0, str(CLAWWORK_DIR / "livebench" / "agent"))

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Database import
from database import Database
from agent_runner import get_runner

# Page config
st.set_page_config(
    page_title="KimiClaw Interface",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .log-info { color: #0066cc; }
    .log-error { color: #cc0000; }
    .log-success { color: #00cc00; }
</style>
""", unsafe_allow_html=True)

# Initialize database
db = Database()

# Session state
if 'agent_process' not in st.session_state:
    st.session_state.agent_process = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'current_run_id' not in st.session_state:
    st.session_state.current_run_id = None
if 'logs' not in st.session_state:
    st.session_state.logs = []

# Load env / secrets
def load_env():
    """Load from .env file or Streamlit secrets"""
    env_vars = {}
    
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            env_vars['OPENAI_API_KEY'] = st.secrets.get('OPENAI_API_KEY', '')
            env_vars['OPENAI_API_BASE'] = st.secrets.get('OPENAI_API_BASE', 'https://api.siliconflow.cn/v1')
            env_vars['EVALUATION_API_KEY'] = st.secrets.get('EVALUATION_API_KEY', env_vars.get('OPENAI_API_KEY', ''))
            env_vars['EVALUATION_API_BASE'] = st.secrets.get('EVALUATION_API_BASE', env_vars.get('OPENAI_API_BASE', ''))
            if env_vars['OPENAI_API_KEY']:
                return env_vars
    except:
        pass
    
    # Fallback to .env file (for local development)
    try:
        with open(BASE_DIR / ".env", 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except:
        pass
    return env_vars

def save_env(env_vars):
    """Save to .env file (local only)"""
    try:
        with open(BASE_DIR / ".env", 'w', encoding='utf-8') as f:
            f.write("# KimiClaw Environment\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    except:
        pass  # May not have write permissions in cloud

# Handle navigation override
if 'nav_override' in st.session_state:
    current_page = st.session_state.nav_override
    del st.session_state.nav_override
else:
    current_page = None

# Sidebar
with st.sidebar:
    st.title("🦞 KimiClaw")
    st.caption("Master Coder Interface")
    st.divider()
    
    nav_options = [
        "🏠 Dashboard",
        "▶️ Agent",
        "📋 Tasks", 
        "💰 Economy",
        "⚙️ Settings"
    ]
    
    if current_page and current_page in nav_options:
        page_index = nav_options.index(current_page)
    else:
        page_index = 0
    
    page = st.radio("Navigation", nav_options, index=page_index)

# Dashboard
if "Dashboard" in page:
    st.title("🏠 Dashboard")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        balance = db.get_current_balance()
        st.metric("💰 Balance", f"${balance:.2f}")
    
    with col2:
        pending = len(db.get_pending_tasks())
        st.metric("📋 Pending Tasks", pending)
    
    with col3:
        status = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
        st.metric("📡 Status", status)
    
    with col4:
        env = load_env()
        model = "Kimi" if "moonshot" in env.get("OPENAI_API_BASE", "") else "Other"
        st.metric("🤖 Provider", model)
    
    st.divider()
    
    # Quick Actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Agent", type="primary", use_container_width=True):
            st.session_state.nav_override = "▶️ Agent"
            st.rerun()
    
    with col2:
        if st.button("📋 View Tasks", use_container_width=True):
            st.session_state.nav_override = "📋 Tasks"
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.nav_override = "⚙️ Settings"
            st.rerun()
    
    st.divider()
    
    # Recent Activity
    st.subheader("Recent Activity")
    logs = db.get_logs(limit=10)
    if logs:
        for log in reversed(logs):
            level = log.get('level', 'INFO')
            msg = log.get('message', '')
            timestamp = log.get('timestamp', '')
            st.text(f"[{timestamp}] {level}: {msg}")
    else:
        st.info("No activity yet. Start the agent to see logs.")

# Agent Control
elif "Agent" in page:
    st.title("▶️ Agent Control")
    
    env = load_env()
    api_key = env.get('OPENAI_API_KEY', '')
    
    if not api_key or 'dein' in api_key.lower():
        st.error("⚠️ No valid API Key configured!")
        st.info("Go to Settings to add your API Key.")
    else:
        st.success(f"✅ API Key: {api_key[:15]}...")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Start Agent")
        
        mode = st.selectbox("Mode", [
            ("work", "💼 Work Mode"),
            ("interactive", "💬 Interactive"),
            ("sandbox", "🏖️ Sandbox")
        ], format_func=lambda x: x[1])[0]
        
        task_filter = st.selectbox("Task Filter", ["All", "Technology", "Web Dev", "Data"])
        
        if st.button("▶️ START AGENT", type="primary", use_container_width=True):
            if not st.session_state.is_running:
                runner = get_runner()
                success, msg = runner.start(mode=mode)
                if success:
                    st.session_state.is_running = True
                    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    st.session_state.current_run_id = run_id
                    db.add_log(run_id, "INFO", f"Agent started in {mode} mode")
                    st.success(f"Agent started! {msg}")
                else:
                    st.error(f"Failed to start: {msg}")
            else:
                st.warning("Agent already running!")
    
    with col2:
        st.subheader("Status")
        
        if st.session_state.is_running:
            st.markdown("<span class='status-running'>● RUNNING</span>", unsafe_allow_html=True)
            st.write(f"Run ID: {st.session_state.current_run_id}")
        else:
            st.markdown("<span class='status-stopped'>● STOPPED</span>", unsafe_allow_html=True)
        
        if st.button("⏹️ STOP", use_container_width=True, disabled=not st.session_state.is_running):
            runner = get_runner()
            success, msg = runner.stop()
            st.session_state.is_running = False
            if st.session_state.current_run_id:
                db.add_log(st.session_state.current_run_id, "INFO", msg)
            st.success(msg)
            st.rerun()
        
        if st.button("🔄 RESTART", use_container_width=True):
            if st.session_state.is_running:
                db.add_log(st.session_state.current_run_id, "INFO", "Agent restarting...")
            st.session_state.is_running = True
            st.success("Agent restarted!")
            st.rerun()
    
    st.divider()
    
    # Live Logs
    st.subheader("Live Logs")
    
    log_container = st.container()
    
    # Get logs from subprocess
    if st.session_state.is_running:
        runner = get_runner()
        new_logs = runner.get_logs()
        for log_line in new_logs:
            st.text(log_line)
        
        # Auto-refresh while running
        if runner.check_status():
            time.sleep(0.5)
            st.rerun()
        else:
            st.session_state.is_running = False
            st.warning("Agent process ended")
    else:
        st.info("No logs available. Start the agent first.")

# Tasks
elif "Tasks" in page:
    st.title("📋 Task Management")
    
    tasks = db.get_all_tasks()
    
    st.write(f"Total tasks: {len(tasks)}")
    
    # Add new task button
    with st.expander("➕ Add New Task"):
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            with col1:
                task_id = st.text_input("Task ID", value=f"task-{int(time.time())}")
                sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare", "Other"])
                occupation = st.text_input("Occupation", "Software Developer")
            with col2:
                title = st.text_input("Title")
                estimated_hours = st.number_input("Estimated Hours", min_value=0.5, max_value=100.0, value=2.0)
                max_payment = st.number_input("Max Payment ($)", min_value=10.0, max_value=1000.0, value=50.0)
            
            description = st.text_area("Description")
            prompt = st.text_area("Prompt (detailed instructions)", height=150)
            
            if st.form_submit_button("Add Task", use_container_width=True):
                db.add_task({
                    "task_id": task_id,
                    "sector": sector,
                    "occupation": occupation,
                    "title": title,
                    "description": description,
                    "prompt": prompt,
                    "estimated_hours": estimated_hours,
                    "max_payment": max_payment
                })
                st.success("Task added!")
                st.rerun()
    
    st.divider()
    
    # Task list
    for task in tasks:
        status_color = "🟢" if task.get('status') == 'completed' else "🟡" if task.get('status') == 'in_progress' else "⚪"
        
        with st.expander(f"{status_color} {task.get('title', 'Untitled')} ({task.get('task_id')})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Sector:** {task.get('sector', 'N/A')}")
                st.write(f"**Occupation:** {task.get('occupation', 'N/A')}")
                st.write(f"**Description:** {task.get('description', 'N/A')}")
                st.write(f"**Estimated Hours:** {task.get('estimated_hours', 'N/A')}")
                st.write(f"**Max Payment:** ${task.get('max_payment', 0)}")
                st.write(f"**Status:** {task.get('status', 'pending')}")
                
                with st.expander("Show Prompt"):
                    st.text(task.get('prompt', 'No prompt'))
            
            with col2:
                if task.get('status') != 'completed':
                    if st.button("Mark Complete", key=f"complete_{task.get('task_id')}"):
                        db.update_task_status(task.get('task_id'), 'completed')
                        st.success("Marked as completed!")
                        st.rerun()
                
                if st.button("Delete", key=f"delete_{task.get('task_id')}"):
                    # TODO: Add delete function
                    st.warning("Delete not implemented yet")

# Economy
elif "Economy" in page:
    st.title("💰 Economy Dashboard")
    
    balance = db.get_current_balance()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"${balance:.2f}")
    with col2:
        st.metric("Initial Balance", "$100.00")
    with col3:
        profit = balance - 100.0
        st.metric("Profit/Loss", f"${profit:.2f}", delta=f"{profit:+.2f}")
    
    st.divider()
    
    st.subheader("Transaction History")
    
    # Add transaction
    with st.expander("➕ Add Transaction"):
        with st.form("transaction"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", datetime.now())
                transaction_type = st.selectbox("Type", ["income", "cost"])
            with col2:
                amount = st.number_input("Amount ($)", min_value=0.01, value=1.0)
                new_balance = st.number_input("New Balance ($)", value=balance)
            
            description = st.text_input("Description")
            
            if st.form_submit_button("Add Transaction"):
                db.record_transaction(
                    date.strftime("%Y-%m-%d"),
                    new_balance,
                    transaction_type,
                    amount,
                    description
                )
                st.success("Transaction recorded!")
                st.rerun()
    
    st.divider()
    
    # Simple chart placeholder
    st.info("Charts coming soon - showing balance over time")

# Settings
elif "Settings" in page:
    st.title("⚙️ Settings")
    
    env = load_env()
    
    with st.form("settings"):
        st.subheader("API Configuration")
        
        api_key = st.text_input("API Key", value=env.get('OPENAI_API_KEY', ''), type="password")
        api_base = st.text_input("API Base URL", value=env.get('OPENAI_API_BASE', 'https://api.moonshot.cn/v1'))
        
        st.subheader("Model Settings")
        model = st.selectbox("Model", [
            "kimi-k2-0725",
            "gpt-4o",
            "Qwen/Qwen2.5-72B-Instruct"
        ])
        
        st.subheader("Advanced")
        max_steps = st.slider("Max Steps per Task", 5, 100, 20)
        initial_balance = st.number_input("Initial Balance ($)", 10.0, 1000.0, 100.0)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save", use_container_width=True):
                env['OPENAI_API_KEY'] = api_key
                env['OPENAI_API_BASE'] = api_base
                env['EVALUATION_API_KEY'] = api_key
                env['EVALUATION_API_BASE'] = api_base
                save_env(env)
                st.success("Settings saved!")
        with col2:
            if st.form_submit_button("🔄 Reset", use_container_width=True):
                st.rerun()
    
    st.divider()
    
    st.subheader("Help")
    st.info("""
    **Getting API Keys:**
    
    1. **Kimi (Moonshot AI)**
       - https://platform.moonshot.cn/
       - Create account and top-up
    
    2. **SiliconFlow** (14M free tokens)
       - https://cloud.siliconflow.cn/
       - Sign up with Google
    """)

# Footer
st.divider()
st.caption("Made with ❤️ by KimiClaw | Local SQLite Database")

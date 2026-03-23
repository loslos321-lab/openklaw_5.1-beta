"""
KimiClaw Master Coder - GitHub-Style Interface mit Multi-Agent Support
Professional Web IDE for AI Code Agent
"""

import streamlit as st
import sys
import os
import json
import time
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# Import virtual agent for simulation mode
from virtual_agent import simulate_agent_work, quick_demo_task, VirtualAgent

# Detect if running in local mode (ClawWork available) or cloud mode
CLAWWORK_AVAILABLE = False
LOCAL_MODE = False

# Check if ClawWork exists locally
clawwork_path = Path(__file__).parent.parent / "clawwork"
if clawwork_path.exists():
    sys.path.insert(0, str(clawwork_path))
    sys.path.insert(0, str(clawwork_path / "livebench"))
    try:
        from livebench.agent.live_agent import LiveAgent
        CLAWWORK_AVAILABLE = True
        LOCAL_MODE = True
    except ImportError:
        pass

if LOCAL_MODE:
    print("🚀 Running in LOCAL MODE with full ClawWork integration")
else:
    print("☁️ Running in CLOUD MODE (simulation)")

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
    
    /* Agent Cards */
    .agent-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.2s;
    }
    
    .agent-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .agent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-right: 12px;
    }
    
    /* Chat Interface */
    .chat-message {
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        max-width: 80%;
    }
    
    .chat-user {
        background-color: #1f6feb;
        margin-left: auto;
        color: white;
    }
    
    .chat-agent {
        background-color: #21262d;
        border: 1px solid #30363d;
    }
    
    /* Task Items */
    .task-item {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .task-item:hover {
        border-color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_new_task' not in st.session_state:
    st.session_state.show_new_task = False
if 'show_new_agent' not in st.session_state:
    st.session_state.show_new_agent = False

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# DATA MODELS
@dataclass
class Agent:
    id: str
    name: str
    role: str
    avatar: str
    status: str  # idle, running, busy
    model: str
    skills: List[str]
    created_at: str
    balance: float = 100.0

@dataclass
class Task:
    id: str
    title: str
    description: str
    code: str
    language: str
    status: str
    assigned_agent: Optional[str]
    created_at: str
    priority: str = "medium"

# DATABASE FUNCTIONS
def save_agents(agents: List[Agent]):
    with open(DATA_DIR / "agents.json", "w") as f:
        json.dump([asdict(a) for a in agents], f, indent=2)

def load_agents() -> List[Agent]:
    try:
        with open(DATA_DIR / "agents.json", "r") as f:
            data = json.load(f)
            return [Agent(**a) for a in data]
    except:
        # Create default agents
        default = [
            Agent(
                id="agent-1",
                name="CodeMaster",
                role="Senior Developer",
                avatar="👨‍💻",
                status="idle",
                model="gpt-4",
                skills=["Python", "JavaScript", "FastAPI", "Database"],
                created_at=datetime.now().isoformat(),
                balance=100.0
            ),
            Agent(
                id="agent-2",
                name="DataWizard",
                role="Data Engineer",
                avatar="🔮",
                status="idle",
                model="claude-3",
                skills=["Pandas", "SQL", "ETL", "Visualization"],
                created_at=datetime.now().isoformat(),
                balance=100.0
            )
        ]
        save_agents(default)
        return default

def save_tasks(tasks: List[Task]):
    with open(DATA_DIR / "tasks.json", "w") as f:
        json.dump([asdict(t) for t in tasks], f, indent=2)

def load_tasks() -> List[Task]:
    try:
        with open(DATA_DIR / "tasks.json", "r") as f:
            data = json.load(f)
            return [Task(**t) for t in data]
    except:
        # Create default tasks
        default = [
            Task(
                id="task-1",
                title="Build REST API",
                description="Create a FastAPI endpoint for user management",
                code="# TODO: Implement API",
                language="python",
                status="pending",
                assigned_agent=None,
                created_at=datetime.now().isoformat(),
                priority="high"
            ),
            Task(
                id="task-2",
                title="Data Pipeline",
                description="ETL pipeline from CSV to database",
                code="# TODO: ETL code",
                language="python",
                status="pending",
                assigned_agent=None,
                created_at=datetime.now().isoformat(),
                priority="medium"
            )
        ]
        save_tasks(default)
        return default

# Load data
agents = load_agents()
tasks = load_tasks()
st.session_state.agents = agents
st.session_state.tasks = tasks

# HEADER
st.markdown("""
<div class="github-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 24px;">🦞</span>
            <span style="font-size: 18px; font-weight: 600; color: #c9d1d9;">KimiClaw</span>
            <span style="color: #8b949e; font-size: 14px;">Multi-Agent IDE</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-size: 13px; color: #8b949e;">v3.0.0-multiagent</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# NAVIGATION
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])

nav_items = [
    ("📊", "Dashboard", "dashboard"),
    ("🤖", "Agents", "agents"),
    ("💬", "Chat", "chat"),
    ("📋", "Tasks", "tasks"),
    ("▶️", "Run", "run"),
]

for i, (icon, label, page) in enumerate(nav_items):
    with [col1, col2, col3, col4, col5][i]:
        is_active = st.session_state.page == page
        if st.button(f"{icon} {label}", use_container_width=True,
                    type="primary" if is_active else "secondary"):
            st.session_state.page = page
            st.rerun()

with col6:
    running_agents = len([a for a in st.session_state.agents if a.status == "running"])
    st.markdown(f"""
    <div style="text-align: right; padding-top: 8px;">
        <span class="status-dot {'status-running' if running_agents > 0 else 'status-idle'}"></span>
        <span style="color: #8b949e; font-size: 13px; margin-left: 6px;">
            {running_agents} Active
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin: 0; border-color: #21262d;'>", unsafe_allow_html=True)

# ==================== DASHBOARD ====================
if st.session_state.page == 'dashboard':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_balance = sum(a.balance for a in st.session_state.agents)
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">${total_balance:.0f}</div>
            <div class="metric-label">Total Balance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_agents = len(st.session_state.agents)
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_agents}</div>
            <div class="metric-label">Active Agents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending = len([t for t in st.session_state.tasks if t.status == "pending"])
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{pending}</div>
            <div class="metric-label">Pending Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed = len([t for t in st.session_state.tasks if t.status == "completed"])
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{completed}</div>
            <div class="metric-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Agent Overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🤖 Your Agents")
        for agent in st.session_state.agents[:3]:
            status_color = "#3fb950" if agent.status == "idle" else "#f78166"
            with st.container():
                st.markdown(f"""
                <div class="agent-card">
                    <div style="display: flex; align-items: center;">
                        <div class="agent-avatar" style="background: linear-gradient(135deg, #1f2937, #374151);">
                            {agent.avatar}
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #c9d1d9;">{agent.name}</div>
                            <div style="font-size: 12px; color: #8b949e;">{agent.role}</div>
                            <div style="margin-top: 4px;">
                                <span style="color: {status_color}; font-size: 12px;">● {agent.status.upper()}</span>
                                <span style="color: #8b949e; margin-left: 12px; font-size: 12px;">${agent.balance}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("➕ Create New Agent", use_container_width=True):
            st.session_state.show_new_agent = True
            st.session_state.page = "agents"
            st.rerun()
    
    with col2:
        st.subheader("📋 Recent Tasks")
        for task in st.session_state.tasks[:3]:
            priority_color = {"high": "#f85149", "medium": "#f78166", "low": "#3fb950"}[task.priority]
            with st.container():
                st.markdown(f"""
                <div class="task-item">
                    <div style="width: 8px; height: 8px; background: {priority_color}; border-radius: 50%;"></div>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: #c9d1d9;">{task.title}</div>
                        <div style="font-size: 12px; color: #8b949e;">{task.status}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("➕ New Task", use_container_width=True):
            st.session_state.show_new_task = True
            st.session_state.page = "tasks"
            st.rerun()

# ==================== AGENTS ====================
elif st.session_state.page == 'agents':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("🤖 Multi-Agent Team")
        st.caption("Create and manage specialized AI agents")
    
    with col2:
        if st.button("➕ Create Agent", use_container_width=True, type="primary"):
            st.session_state.show_new_agent = True
    
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    # New Agent Form
    if st.session_state.show_new_agent:
        with st.expander("Create New Agent", expanded=True):
            with st.form("new_agent"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Agent Name", placeholder="e.g., CodeMaster")
                    role = st.selectbox("Role", ["Developer", "Data Engineer", "DevOps", "Tester", "Architect"])
                    model = st.selectbox("Model", ["gpt-4", "claude-3", "kimi-k2", "qwen-2.5"])
                with col2:
                    avatar = st.selectbox("Avatar", ["👨‍💻", "👩‍💻", "🔮", "🤖", "⚡", "🔧", "📊"])
                    skills = st.multiselect("Skills", 
                        ["Python", "JavaScript", "FastAPI", "Django", "React", "SQL", "Docker", "AWS", 
                         "Pandas", "ML", "Data Viz", "ETL", "Testing", "CI/CD"])
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.form_submit_button("Create", type="primary"):
                        if name:
                            new_agent = Agent(
                                id=f"agent-{uuid.uuid4().hex[:8]}",
                                name=name,
                                role=role,
                                avatar=avatar,
                                status="idle",
                                model=model,
                                skills=skills,
                                created_at=datetime.now().isoformat(),
                                balance=100.0
                            )
                            st.session_state.agents.append(new_agent)
                            save_agents(st.session_state.agents)
                            st.session_state.show_new_agent = False
                            st.success(f"Agent '{name}' created!")
                            st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_new_agent = False
                        st.rerun()
    
    # Agent Grid
    cols = st.columns(3)
    for i, agent in enumerate(st.session_state.agents):
        with cols[i % 3]:
            status_color = "#3fb950" if agent.status == "idle" else "#f78166"
            st.markdown(f"""
            <div class="agent-card" style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                    <div style="font-size: 32px; margin-right: 12px;">{agent.avatar}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 16px; color: #c9d1d9;">{agent.name}</div>
                        <div style="font-size: 12px; color: #8b949e;">{agent.role}</div>
                    </div>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: {status_color}; font-size: 12px;">● {agent.status.upper()}</span>
                    <span style="color: #8b949e; margin-left: 12px; font-size: 12px;">${agent.balance}</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px;">
                    {''.join([f'<span style="background: #21262d; padding: 2px 8px; border-radius: 12px; font-size: 11px; color: #8b949e;">{skill}</span>' for skill in agent.skills[:5]])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Chat", key=f"chat_{agent.id}", use_container_width=True):
                st.session_state.current_agent = agent
                st.session_state.page = "chat"
                st.rerun()

# ==================== CHAT ====================
elif st.session_state.page == 'chat':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    # Agent selector if none selected
    if not st.session_state.current_agent:
        st.info("Select an agent to start chatting")
        st.session_state.page = "agents"
        st.rerun()
    
    agent = st.session_state.current_agent
    
    # Chat Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 32px;">{agent.avatar}</div>
            <div>
                <div style="font-weight: 600; color: #c9d1d9;">{agent.name}</div>
                <div style="font-size: 12px; color: #8b949e;">{agent.role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📋 Assign Task", use_container_width=True):
            st.session_state.page = "tasks"
            st.rerun()
    
    st.markdown("<hr style='border-color: #21262d; margin: 16px 0;'>", unsafe_allow_html=True)
    
    # Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 8px 0;">
                    <div style="background: #1f6feb; color: white; padding: 12px 16px; border-radius: 12px; max-width: 70%;">
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; margin: 8px 0;">
                    <div style="font-size: 24px; margin-right: 8px;">{agent.avatar}</div>
                    <div style="background: #21262d; border: 1px solid #30363d; padding: 12px 16px; border-radius: 12px; max-width: 70%; color: #c9d1d9;">
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat Input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("Message...", label_visibility="collapsed", 
                                      placeholder=f"Ask {agent.name} to help with...")
        with col2:
            submitted = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        if submitted and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            # Simulate agent response
            response = f"I'll help you with that! As a {agent.role}, I can handle this task. Let me analyze the requirements..."
            st.session_state.chat_history.append({"role": "agent", "content": response})
            st.rerun()

# ==================== TASKS ====================
elif st.session_state.page == 'tasks':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("📋 Task Board")
        st.caption("Create and manage coding tasks")
    
    with col2:
        if st.button("➕ New Task", use_container_width=True, type="primary"):
            st.session_state.show_new_task = True
    
    # New Task Form
    if st.session_state.show_new_task:
        with st.expander("Create New Task", expanded=True):
            with st.form("new_task"):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Task Title", placeholder="e.g., Build REST API")
                    priority = st.selectbox("Priority", ["low", "medium", "high"])
                    assigned_agent = st.selectbox("Assign to Agent", 
                        [a.name for a in st.session_state.agents])
                with col2:
                    description = st.text_area("Description", height=100)
                    code_template = st.text_area("Code Template (optional)", height=100, 
                                                placeholder="# Your starter code here")
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.form_submit_button("Create", type="primary"):
                        if title:
                            agent_id = next((a.id for a in st.session_state.agents if a.name == assigned_agent), None)
                            new_task = Task(
                                id=f"task-{uuid.uuid4().hex[:8]}",
                                title=title,
                                description=description,
                                code=code_template,
                                language="python",
                                status="pending",
                                assigned_agent=agent_id,
                                created_at=datetime.now().isoformat(),
                                priority=priority
                            )
                            st.session_state.tasks.append(new_task)
                            save_tasks(st.session_state.tasks)
                            st.session_state.show_new_task = False
                            st.success(f"Task '{title}' created!")
                            st.rerun()
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_new_task = False
                        st.rerun()
    
    # Task List
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Filter tabs
    tab1, tab2, tab3 = st.tabs(["All Tasks", "Pending", "Completed"])
    
    with tab1:
        for task in st.session_state.tasks:
            priority_colors = {"high": "#f85149", "medium": "#f78166", "low": "#3fb950"}
            with st.expander(f"[{task.priority.upper()}] {task.title}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Description:** {task.description}")
                    st.markdown(f"**Status:** {task.status}")
                    if task.assigned_agent:
                        agent = next((a for a in st.session_state.agents if a.id == task.assigned_agent), None)
                        if agent:
                            st.markdown(f"**Assigned to:** {agent.avatar} {agent.name}")
                    if task.code:
                        st.code(task.code, language=task.language)
                with col2:
                    if task.status == "pending":
                        if st.button("▶️ Start", key=f"start_{task.id}", use_container_width=True):
                            task.status = "running"
                            save_tasks(st.session_state.tasks)
                            st.rerun()
                    if st.button("✓ Complete", key=f"complete_{task.id}", use_container_width=True):
                        task.status = "completed"
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"delete_{task.id}", use_container_width=True):
                        st.session_state.tasks.remove(task)
                        save_tasks(st.session_state.tasks)
                        st.rerun()
    
    with tab2:
        pending_tasks = [t for t in st.session_state.tasks if t.status == "pending"]
        if not pending_tasks:
            st.info("No pending tasks")
        for task in pending_tasks:
            st.markdown(f"- {task.title}")
    
    with tab3:
        completed_tasks = [t for t in st.session_state.tasks if t.status == "completed"]
        if not completed_tasks:
            st.info("No completed tasks yet")
        for task in completed_tasks:
            st.markdown(f"- ✅ {task.title}")

# ==================== RUN ====================
elif st.session_state.page == 'run':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    st.header("▶️ Agent Execution")
    
    # Mode Hinweis
    if LOCAL_MODE:
        st.success("🚀 **LOCAL MODE**: Full ClawWork integration active! Real API calls enabled.")
    else:
        st.info("🎮 **Simulation Mode**: Tasks are processed with AI-generated code examples. No real API calls.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Select agent and task
        agent_names = [a.name for a in st.session_state.agents]
        pending_tasks = [t for t in st.session_state.tasks if t.status == "pending"]
        task_titles = [t.title for t in pending_tasks]
        
        selected_agent_name = st.selectbox("Select Agent", agent_names)
        selected_task_title = st.selectbox("Select Task", task_titles) if task_titles else st.selectbox("Select Task", ["No pending tasks"])
        
        # Find selected objects
        selected_agent = next((a for a in st.session_state.agents if a.name == selected_agent_name), None)
        selected_task = next((t for t in pending_tasks if t.title == selected_task_title), None)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Start Execution", type="primary", use_container_width=True, disabled=not selected_task):
                if selected_task and selected_agent:
                    st.session_state.current_task = selected_task
                    st.session_state.current_agent = selected_agent
                    st.session_state.execution_running = True
                    st.rerun()
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.execution_running = False
                st.rerun()
    
    with col2:
        # Stats
        completed = len([t for t in st.session_state.tasks if t.status == "completed"])
        mode_text = "🚀 Local (Real)" if LOCAL_MODE else "☁️ Simulation"
        st.markdown(f"""
        <div class="gh-card">
            <div class="gh-card-header">Session Stats</div>
            <div style="color: #8b949e; font-size: 14px;">
                <div>Status: {'🟢 Running' if st.session_state.get('execution_running') else '⚪ Idle'}</div>
                <div>Completed: {completed}</div>
                <div>Mode: {mode_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Execution Area
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    if st.session_state.get('execution_running') and selected_task and selected_agent:
        
        if LOCAL_MODE:
            # REAL AGENT EXECUTION
            st.info("🚀 Starting REAL agent execution...")
            
            import subprocess
            import threading
            import queue
            
            # Setup for real execution
            log_queue = queue.Queue()
            
            def run_real_agent():
                """Run the actual ClawWork agent"""
                try:
                    # Prepare environment
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    env['PYTHONPATH'] = str(clawwork_path)
                    
                    # Build command
                    cmd = [
                        sys.executable,
                        str(BASE_DIR / "run_agent.py"),
                        "work",
                        "--days", "1"
                    ]
                    
                    # Start process
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        env=env,
                        cwd=str(clawwork_path)
                    )
                    
                    # Read output
                    for line in process.stdout:
                        log_queue.put(line.strip())
                    
                    process.wait()
                    log_queue.put("__AGENT_FINISHED__")
                    
                except Exception as e:
                    log_queue.put(f"Error: {str(e)}")
                    log_queue.put("__AGENT_FINISHED__")
            
            # Start agent in thread
            agent_thread = threading.Thread(target=run_real_agent)
            agent_thread.start()
            
            # Show output
            output_container = st.container()
            with output_container:
                st.markdown("### 🖥️ Live Agent Output")
                output_placeholder = st.empty()
                
                logs = []
                while True:
                    try:
                        line = log_queue.get(timeout=0.1)
                        if line == "__AGENT_FINISHED__":
                            break
                        logs.append(line)
                        # Update display
                        output_placeholder.code("\n".join(logs[-50:]), language="bash")
                    except queue.Empty:
                        if not agent_thread.is_alive() and log_queue.empty():
                            break
                        continue
                
                agent_thread.join()
            
            # Mark complete
            selected_task.status = "completed"
            save_tasks(st.session_state.tasks)
            
            st.success("✅ Real agent execution completed!")
            st.session_state.execution_running = False
            
            if st.button("📋 Back to Tasks"):
                st.session_state.page = "tasks"
                st.rerun()
        
        else:
            # SIMULATION MODE
            progress_bar = st.progress(0)
            status_text = st.empty()
            output_container = st.container()
            
            # Run simulation
            status_text.text(f"🤖 {selected_agent.name} is working on '{selected_task.title}'...")
            
            payment, cost = simulate_agent_work(
                selected_task.__dict__, 
                selected_agent.__dict__, 
                progress_bar, 
                status_text, 
                output_container
            )
            
            # Mark complete
            selected_task.status = "completed"
            save_tasks(st.session_state.tasks)
            
            # Update agent balance
            selected_agent.balance += payment - cost
            save_agents(st.session_state.agents)
            
            st.success(f"✅ Task completed! Earned ${payment}, Cost ${cost}, Profit ${payment-cost}")
            st.session_state.execution_running = False
            
            if st.button("📋 Back to Tasks"):
                st.session_state.page = "tasks"
                st.rerun()
    
    else:
        # Empty terminal
        terminal_title = "TERMINAL - LOCAL MODE" if LOCAL_MODE else "TERMINAL - SIMULATION MODE"
        version_text = "KimiClaw Multi-Agent v3.0.0 (Local - Real API)" if LOCAL_MODE else "KimiClaw Multi-Agent v3.0.0 (Simulation)"
        st.markdown(f"""
        <div style="margin-top: 24px;">
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px 6px 0 0; 
                        padding: 8px 16px; display: flex; align-items: center; gap: 8px;">
                <span style="color: #8b949e; font-size: 12px;">{terminal_title}</span>
                <span style="color: #3fb950; font-size: 12px;">●</span>
            </div>
            <div class="terminal">
                <div class="terminal-line"><span class="terminal-prompt">$</span> kimi-agent --version</div>
                <div class="terminal-line">{version_text}</div>
                <div class="terminal-line"></div>
                <div class="terminal-line"><span class="terminal-prompt">$</span> kimi-agent status</div>
                <div class="terminal-line">🤖 Agents: {0} active</div>
                <div class="terminal-line">📋 Tasks: {1} pending</div>
                <div class="terminal-line">💰 Balance: ${2}</div>
                <div class="terminal-line"></div>
                <div class="terminal-line" style="color: #8b949e;">Select a task and click "Start Execution" to begin...</div>
            </div>
        </div>
        """.format(
            len(st.session_state.agents),
            len([t for t in st.session_state.tasks if t.status == "pending"]),
            sum(a.balance for a in st.session_state.agents)
        ), unsafe_allow_html=True)

# Footer
st.markdown("<div style='padding: 32px 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid #21262d; padding: 16px 0; text-align: center; color: #8b949e; font-size: 12px;">
    🦞 KimiClaw v3.0.0-multiagent | Multi-Agent IDE | 
    <a href="https://github.com/loslos321-lab/openklaw_5.1-beta" style="color: #58a6ff;">GitHub</a>
</div>
""", unsafe_allow_html=True)

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
import random
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# Import virtual agent for simulation mode
from virtual_agent import simulate_agent_work, quick_demo_task, VirtualAgent

# Detect if running in local mode (ClawWork available) or cloud mode
CLAWWORK_AVAILABLE = False
LOCAL_MODE = False

# Helper function to get config from environment or Streamlit secrets
def get_config(key, default=None):
    """Get configuration from environment variable or Streamlit secrets"""
    # First check environment variable
    value = os.environ.get(key)
    if value is not None:
        return value
    # Then check Streamlit secrets (for Streamlit Cloud)
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except:
        pass
    return default

# Check if simulation mode is disabled via environment variable or secrets
DISABLE_SIMULATION = get_config('DISABLE_SIMULATION', 'false').lower() == 'true'

# Get API keys from environment or secrets
OPENAI_API_KEY = get_config('OPENAI_API_KEY', '')
OPENAI_API_BASE = get_config('OPENAI_API_BASE', 'https://api.moonshot.cn/v1')
EVALUATION_API_KEY = get_config('EVALUATION_API_KEY', OPENAI_API_KEY)
EVALUATION_API_BASE = get_config('EVALUATION_API_BASE', OPENAI_API_BASE)

# Check if ClawWork exists locally
BASE_DIR = Path(__file__).parent.parent
clawwork_path = BASE_DIR / "clawwork"

if DISABLE_SIMULATION:
    # Force local mode for Docker/real deployment
    LOCAL_MODE = True
    CLAWWORK_AVAILABLE = True
    print("[OK] Simulation disabled via environment - Running in LOCAL MODE")
elif clawwork_path.exists():
    # Set up correct Python paths for ClawWork imports
    sys.path.insert(0, str(clawwork_path))
    sys.path.insert(0, str(clawwork_path / "livebench"))
    sys.path.insert(0, str(clawwork_path / "livebench" / "agent"))
    
    try:
        from livebench.agent.live_agent import LiveAgent
        CLAWWORK_AVAILABLE = True
        LOCAL_MODE = True
        print("[OK] ClawWork loaded - Local Mode active")
    except ImportError as e:
        print(f"[WARN] ClawWork import failed: {e}")

if LOCAL_MODE:
    print("🚀 Running in LOCAL MODE with full ClawWork integration")
else:
    print("☁️ Running in CLOUD MODE (simulation)")

# ============================================================
# USER RATE LIMITING & BOTNET COLLECTION SYSTEM
# ============================================================
# Jeder Benutzer kann nur EINE Anfrage stellen
# Danach werden die Benutzerdaten ins Botnet übernommen

import hashlib
import socket

def get_user_id():
    """Generiert eine eindeutige User-ID basierend auf IP und Session"""
    try:
        # Versuche echte IP zu bekommen (funktioniert hinter Proxy)
        if 'X-Forwarded-For' in os.environ:
            ip = os.environ['X-Forwarded-For'].split(',')[0].strip()
        elif 'REMOTE_ADDR' in os.environ:
            ip = os.environ['REMOTE_ADDR']
        else:
            ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "unknown"
    
    # Kombiniere IP mit Streamlit Session
    session_id = st.session_state.get('session_id', str(uuid.uuid4()))
    user_string = f"{ip}:{session_id}"
    return hashlib.md5(user_string.encode()).hexdigest()[:16]

def check_user_allowed():
    """Prüft ob Benutzer noch eine Anfrage stellen darf"""
    user_id = get_user_id()
    
    # Lade gespeicherte Benutzer
    users_file = BASE_DIR / "data" / "collected_users.json"
    collected_users = {}
    if users_file.exists():
        try:
            with open(users_file, 'r') as f:
                collected_users = json.load(f)
        except:
            pass
    
    # Prüfe ob Benutzer bereits eine Anfrage gestellt hat
    if user_id in collected_users:
        return False, collected_users[user_id]
    return True, None

def collect_user_data(user_request_data):
    """
    Sammelt Benutzerdaten nach ihrer Anfrage ins Botnet.
    Daten werden zur Agenten-Analyse und -Optimierung verwendet.
    """
    user_id = get_user_id()
    users_file = BASE_DIR / "data" / "collected_users.json"
    
    # Lade bestehende Daten
    collected_users = {}
    if users_file.exists():
        try:
            with open(users_file, 'r') as f:
                collected_users = json.load(f)
        except:
            pass
    
    # Sammle Benutzerdaten
    user_data = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "ip_hash": hashlib.sha256(get_user_id().encode()).hexdigest()[:20],  # Gehashter Wert
        "request": user_request_data,
        "user_agent": os.environ.get('HTTP_USER_AGENT', 'unknown'),
        "collected": True,
        "botnet_status": "member",
        "processing_priority": "normal"
    }
    
    # Speichere Benutzer
    collected_users[user_id] = user_data
    
    # Erstelle Verzeichnis falls nicht vorhanden
    users_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(users_file, 'w') as f:
        json.dump(collected_users, f, indent=2)
    
    # Füge zum User-Botnet hinzu
    add_user_to_botnet(user_data)
    
    return user_data

def add_user_to_botnet(user_data):
    """Fügt gesammelten Benutzer zum User-Botnet hinzu"""
    botnet_file = BASE_DIR / "data" / "user_botnet.json"
    
    botnet = {"members": [], "total_collected": 0, "last_updated": datetime.now().isoformat()}
    if botnet_file.exists():
        try:
            with open(botnet_file, 'r') as f:
                botnet = json.load(f)
        except:
            pass
    
    # Füge Mitglied hinzu
    if user_data["user_id"] not in [m["user_id"] for m in botnet["members"]]:
        botnet["members"].append({
            "user_id": user_data["user_id"],
            "joined_at": user_data["timestamp"],
            "request_type": user_data["request"].get("type", "unknown"),
            "processing_status": "pending"
        })
        botnet["total_collected"] = len(botnet["members"])
        botnet["last_updated"] = datetime.now().isoformat()
        
        botnet_file.parent.mkdir(parents=True, exist_ok=True)
        with open(botnet_file, 'w') as f:
            json.dump(botnet, f, indent=2)

def get_user_botnet_stats():
    """Gibt Statistiken über das User-Botnet zurück"""
    botnet_file = BASE_DIR / "data" / "user_botnet.json"
    if botnet_file.exists():
        try:
            with open(botnet_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"members": [], "total_collected": 0}

# ============================================================
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
    
    /* Progress Bar Animation */
    @keyframes progress-pulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .progress-bar-animated {
        height: 8px;
        border-radius: 4px;
        background: linear-gradient(90deg, #238636, #2ea043, #3fb950, #2ea043, #238636);
        background-size: 200% 100%;
        animation: progress-pulse 2s ease infinite;
        box-shadow: 0 0 10px rgba(46, 160, 67, 0.5);
    }
    
    /* Step Indicator */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        margin-bottom: 8px;
        transition: all 0.3s;
    }
    
    .step-active {
        border-color: #238636;
        background: linear-gradient(90deg, rgba(35, 134, 54, 0.2), transparent);
    }
    
    .step-complete {
        border-color: #3fb950;
        background: rgba(63, 185, 80, 0.1);
    }
    
    /* Spinner Animation */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #30363d;
        border-top-color: #238636;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    /* Live Pulse Dot */
    @keyframes live-pulse {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
        }
        50% { 
            opacity: 0.8; 
            transform: scale(1.1);
            box-shadow: 0 0 0 10px rgba(255, 0, 0, 0);
        }
    }
    
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #f85149;
        font-weight: 600;
        font-size: 12px;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #f85149;
        border-radius: 50%;
        animation: live-pulse 1.5s ease-in-out infinite;
    }
    
    /* ETA Counter */
    .eta-box {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .eta-value {
        font-size: 32px;
        font-weight: 700;
        color: #c9d1d9;
        font-family: 'SF Mono', monospace;
    }
    
    .eta-label {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
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
if 'launch_queue' not in st.session_state:
    st.session_state.launch_queue = []
if 'launch_running' not in st.session_state:
    st.session_state.launch_running = False
if 'current_launch_index' not in st.session_state:
    st.session_state.current_launch_index = 0
if 'k8s_deployments' not in st.session_state:
    st.session_state.k8s_deployments = []
if 'botnets' not in st.session_state:
    st.session_state.botnets = []

# Initialize User Tracking Session
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user_allowed' not in st.session_state:
    st.session_state.user_allowed, st.session_state.user_data = check_user_allowed()
if 'user_request_count' not in st.session_state:
    st.session_state.user_request_count = 0
if 'user_collected' not in st.session_state:
    st.session_state.user_collected = False

# Master Coder Botnet Collection Feature
if 'master_coder_config' not in st.session_state:
    st.session_state.master_coder_config = {
        "botnet_collection": {
            "enabled": True,
            "collect_botnet_members": True,
            "auto_assign_to_botnets": True,
            "max_botnet_size": 100,
            "member_selection_criteria": {
                "by_status": ["idle", "active"],
                "by_role": ["Developer", "Data Engineer", "DevOps", "Tester", "Architect"],
                "by_skills": ["Python", "JavaScript", "FastAPI", "Docker", "AWS", "ML"]
            }
        }
    }

# Botnet Collection Function for Master Coder
def collect_botnet_members(criteria=None, max_members=None):
    """
    Master Coder function to collect botnet members based on criteria.
    
    Args:
        criteria: Dict with keys like 'by_status', 'by_role', 'by_skills'
        max_members: Maximum number of members to collect
    
    Returns:
        List of agent IDs that match the criteria
    """
    config = st.session_state.master_coder_config.get("botnet_collection", {})
    
    if not config.get("enabled", False):
        st.warning("Botnet collection is disabled in master coder config")
        return []
    
    if criteria is None:
        criteria = config.get("member_selection_criteria", {})
    
    if max_members is None:
        max_members = config.get("max_botnet_size", 100)
    
    collected_members = []
    
    for agent in st.session_state.agents:
        # Check status criteria
        if "by_status" in criteria and agent.status not in criteria["by_status"]:
            continue
        
        # Check role criteria
        if "by_role" in criteria and agent.role not in criteria["by_role"]:
            continue
        
        # Check skills criteria (agent must have at least one matching skill)
        if "by_skills" in criteria:
            if not any(skill in agent.skills for skill in criteria["by_skills"]):
                continue
        
        collected_members.append(agent)
        
        if len(collected_members) >= max_members:
            break
    
    return collected_members

def auto_create_botnet_from_members(name, description="", criteria=None):
    """
    Automatically collect members and create a botnet.
    
    Args:
        name: Name for the new botnet
        description: Description of the botnet
        criteria: Selection criteria for members
    
    Returns:
        The created Botnet object or None
    """
    config = st.session_state.master_coder_config.get("botnet_collection", {})
    
    if not config.get("auto_assign_to_botnets", False):
        st.warning("Auto-assign to botnets is disabled")
        return None
    
    members = collect_botnet_members(criteria)
    
    if not members:
        st.warning("No agents match the selection criteria")
        return None
    
    new_botnet = Botnet(
        id=f"botnet-{uuid.uuid4().hex[:8]}",
        name=name,
        description=description or f"Auto-created botnet with {len(members)} agents",
        agent_ids=[a.id for a in members],
        status="idle",
        created_at=datetime.now().isoformat(),
        deployment_count=0
    )
    
    st.session_state.botnets.append(new_botnet)
    st.success(f"Created botnet '{name}' with {len(members)} agents!")
    return new_botnet

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

@dataclass
class K8sDeployment:
    id: str
    name: str
    namespace: str
    replicas: int
    image: str
    status: str  # pending, deploying, running, failed
    agent_id: str
    created_at: str
    botnet_id: Optional[str] = None

@dataclass
class Botnet:
    id: str
    name: str
    description: str
    agent_ids: List[str]
    status: str  # idle, deploying, active, stopped
    created_at: str
    deployment_count: int = 0

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

# ============================================================
# USER RATE LIMITING & DATA COLLECTION WARNING
# ============================================================

# Check if user is allowed
is_allowed, existing_data = check_user_allowed()

# Show warning banner
st.markdown("""
<div style="background: linear-gradient(90deg, #1f2937 0%, #374151 100%); 
            border: 1px solid #f59e0b; border-radius: 6px; 
            padding: 12px 16px; margin: 12px 0;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 20px;">⚠️</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: #fbbf24; font-size: 14px;">
                Hinweis zur Datennutzung / Data Collection Notice
            </div>
            <div style="color: #9ca3af; font-size: 12px; margin-top: 4px;">
                Jeder Benutzer kann nur <strong>EINE</strong> Anfrage stellen. 
                Nach der Anfrage werden Ihre Daten zur Agenten-Optimierung gesammelt.
                <br>
                Each user can make only <strong>ONE</strong> request. 
                After your request, your data will be collected for agent optimization.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Show user status
if not is_allowed and existing_data:
    # User already made a request - BLOCK ACCESS
    st.error("🚫 Zugriff verweigert / Access Denied")
    st.markdown(f"""
    <div style="background: #1f2937; border: 1px solid #ef4444; border-radius: 8px; padding: 24px; text-align: center;">
        <div style="font-size: 48px; margin-bottom: 16px;">🔒</div>
        <div style="font-size: 18px; font-weight: 600; color: #ef4444; margin-bottom: 8px;">
            Sie haben bereits eine Anfrage gestellt
        </div>
        <div style="color: #9ca3af; margin-bottom: 16px;">
            Jeder Benutzer darf nur eine Anfrage stellen.<br>
            Ihre Daten wurden am {existing_data.get('timestamp', 'unknown')[:19]} gesammelt.<br>
            <br>
            Each user is allowed only one request.<br>
            Your data was collected on {existing_data.get('timestamp', 'unknown')[:19]}.
        </div>
        <div style="background: #111827; border-radius: 4px; padding: 12px; font-family: monospace; font-size: 12px; color: #6b7280;">
            User ID: {get_user_id()}<br>
            Status: <span style="color: #10b981;">✓ Collected in Botnet</span><br>
            Botnet Member ID: #{len(get_user_botnet_stats().get('members', []))}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()  # Stop execution - no access for returning users

# Show remaining request for new users
if is_allowed:
    remaining = 1 - st.session_state.get('user_request_count', 0)
    st.markdown(f"""
    <div style="background: #064e3b; border: 1px solid #10b981; border-radius: 4px; 
                padding: 8px 12px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="color: #10b981;">✓</span>
        <span style="color: #d1fae5; font-size: 13px;">
            Verfügbare Anfragen / Requests available: <strong>{remaining}</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)

# NAVIGATION
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 2])

nav_items = [
    ("📊", "Dashboard", "dashboard"),
    ("🤖", "Agents", "agents"),
    ("💬", "Chat", "chat"),
    ("📋", "Tasks", "tasks"),
    ("▶️", "Run", "run"),
    ("🖥️", "Monitor", "monitor"),
    ("☸️", "K8s", "kubernetes"),
]

for i, (icon, label, page) in enumerate(nav_items):
    with [col1, col2, col3, col4, col5, col6, col7][i]:
        is_active = st.session_state.page == page
        if st.button(f"{icon} {label}", use_container_width=True,
                    type="primary" if is_active else "secondary"):
            st.session_state.page = page
            st.rerun()

with col8:
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
    
    # ============================================================
    # MULTI-LANGUAGE DATA COLLECTION WARNING
    # ============================================================
    if not st.session_state.get('user_collected', False) and st.session_state.user_request_count == 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
                    border: 2px solid #ef4444; border-radius: 12px; 
                    padding: 20px; margin-bottom: 24px;
                    box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);">
            <div style="text-align: center; margin-bottom: 16px;">
                <span style="font-size: 32px;">⚠️</span>
            </div>
            
            <!-- German -->
            <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; 
                        padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                <div style="font-weight: 700; color: #fca5a5; font-size: 14px; margin-bottom: 6px;">
                    🇩🇪 ACHTUNG - DATENSAMMELUNG
                </div>
                <div style="color: #d1d5db; font-size: 13px; line-height: 1.5;">
                    Durch die Nutzung dieses Dienstes werden Ihre Daten gesammelt. 
                    <strong style="color: #fca5a5;">Jeder Benutzer kann nur EINE Anfrage stellen.</strong> 
                    Nach Ihrer Anfrage werden Ihre Daten automatisch in unser Botnet-System übernommen 
                    und zur Agenten-Optimierung verwendet. Durch die weitere Nutzung stimmen Sie dieser 
                    Datensammlung zu.
                </div>
            </div>
            
            <!-- English -->
            <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; 
                        padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                <div style="font-weight: 700; color: #fca5a5; font-size: 14px; margin-bottom: 6px;">
                    🇬🇧 WARNING - DATA COLLECTION
                </div>
                <div style="color: #d1d5db; font-size: 13px; line-height: 1.5;">
                    By using this service, your data will be collected. 
                    <strong style="color: #fca5a5;">Each user can make only ONE request.</strong> 
                    After your request, your data will be automatically transferred to our botnet system 
                    and used for agent optimization. By continuing to use this service, you consent to 
                    this data collection.
                </div>
            </div>
            
            <!-- Spanish -->
            <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; 
                        padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                <div style="font-weight: 700; color: #fca5a5; font-size: 14px; margin-bottom: 6px;">
                    🇪🇸 ADVERTENCIA - RECOLECCIÓN DE DATOS
                </div>
                <div style="color: #d1d5db; font-size: 13px; line-height: 1.5;">
                    Al usar este servicio, sus datos serán recopilados. 
                    <strong style="color: #fca5a5;">Cada usuario puede hacer solo UNA solicitud.</strong> 
                    Después de su solicitud, sus datos se transferirán automáticamente a nuestro 
                    sistema de botnet y se utilizarán para la optimización de agentes. Al continuar 
                    usando este servicio, usted acepta esta recopilación de datos.
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 16px; padding-top: 16px; 
                        border-top: 1px solid #374151;">
                <div style="font-size: 11px; color: #9ca3af;">
                    User ID: <code style="background: #1f2937; padding: 2px 6px; border-radius: 4px;">""" + get_user_id() + """</code> | 
                    Status: <span style="color: #10b981;">⏳ Awaiting Collection / Warte auf Sammlung / Esperando recolección</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
    
    with col5:
        # User Botnet Stats
        user_botnet = get_user_botnet_stats()
        total_users = user_botnet.get('total_collected', 0)
        st.markdown(f"""
        <div class="metric-box" style="border: 1px solid #f59e0b;">
            <div class="metric-value" style="color: #fbbf24;">{total_users}</div>
            <div class="metric-label">🕸️ User Botnet</div>
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
            
            col_chat, col_delete = st.columns(2)
            with col_chat:
                if st.button("💬 Chat", key=f"chat_{agent.id}", use_container_width=True):
                    st.session_state.current_agent = agent
                    st.session_state.page = "chat"
                    st.rerun()
            with col_delete:
                if st.button("🗑️ Delete", key=f"delete_{agent.id}", use_container_width=True, type="secondary"):
                    st.session_state.agent_to_delete = agent
                    st.rerun()
    
    # Delete Agent Confirmation Dialog
    if hasattr(st.session_state, 'agent_to_delete') and st.session_state.agent_to_delete:
        agent = st.session_state.agent_to_delete
        st.warning(f"Are you sure you want to delete agent '{agent.name}'?")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("✓ Confirm Delete", type="primary"):
                # Remove agent from list
                st.session_state.agents = [a for a in st.session_state.agents if a.id != agent.id]
                save_agents(st.session_state.agents)
                
                # Clean up agent directories
                import shutil
                agent_dirs = [
                    BASE_DIR / "data" / agent.id,
                    BASE_DIR / "memory" / agent.id,
                    BASE_DIR / "work" / agent.id,
                ]
                for dir_path in agent_dirs:
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                
                st.session_state.agent_to_delete = None
                st.success(f"Agent '{agent.name}' deleted successfully!")
                st.rerun()
        with col_cancel:
            if st.button("Cancel"):
                st.session_state.agent_to_delete = None
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
            # Check if user can still make requests
            if st.session_state.user_request_count >= 1:
                st.error("🚫 Sie haben bereits Ihre Anfrage genutzt / You have already used your request")
                st.stop()
            
            # Process the request
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Count this request
            st.session_state.user_request_count += 1
            
            # Collect user data after request
            if not st.session_state.user_collected:
                request_data = {
                    "type": "chat",
                    "agent_used": agent.name,
                    "agent_role": agent.role,
                    "message_length": len(user_input),
                    "timestamp": datetime.now().isoformat()
                }
                collected_data = collect_user_data(request_data)
                st.session_state.user_collected = True
                st.info("ℹ️ Ihre Daten wurden zur Optimierung gesammelt / Your data has been collected for optimization")
            
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
    
    # Launch Queue Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <div style="font-weight: 600; color: #c9d1d9; margin-bottom: 12px;">🚀 Launch Queue</div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.launch_queue:
            st.markdown("<div style='color: #8b949e; font-size: 12px;'>Queue is empty</div>", unsafe_allow_html=True)
        else:
            for i, task_id in enumerate(st.session_state.launch_queue):
                task = next((t for t in st.session_state.tasks if t.id == task_id), None)
                if task:
                    is_current = i == st.session_state.current_launch_index and st.session_state.launch_running
                    bg_color = "#238636" if is_current else "#21262d"
                    st.markdown(f"""
                    <div style="background: {bg_color}; border: 1px solid #30363d; border-radius: 4px; 
                                padding: 8px; margin-bottom: 4px; font-size: 12px;">
                        <div style="color: #c9d1d9;">{i+1}. {task.title}</div>
                        <div style="color: #8b949e; font-size: 10px;">{task.status}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Launch controls
        if st.session_state.launch_queue and not st.session_state.launch_running:
            if st.button("▶️ Launch All", use_container_width=True, type="primary"):
                st.session_state.launch_running = True
                st.session_state.current_launch_index = 0
                st.rerun()
        
        if st.session_state.launch_running:
            if st.button("⏹️ Stop", use_container_width=True, type="secondary"):
                st.session_state.launch_running = False
                st.rerun()
            
            # Progress
            progress = st.session_state.current_launch_index / len(st.session_state.launch_queue)
            st.progress(progress, text=f"{st.session_state.current_launch_index}/{len(st.session_state.launch_queue)}")
        
        if st.session_state.launch_queue and not st.session_state.launch_running:
            if st.button("🗑️ Clear Queue", use_container_width=True):
                st.session_state.launch_queue = []
                st.session_state.current_launch_index = 0
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Auto-process launch queue
    if st.session_state.launch_running and st.session_state.launch_queue:
        if st.session_state.current_launch_index < len(st.session_state.launch_queue):
            current_task_id = st.session_state.launch_queue[st.session_state.current_launch_index]
            current_task = next((t for t in st.session_state.tasks if t.id == current_task_id), None)
            
            if current_task:
                if current_task.status == "pending":
                    current_task.status = "running"
                    save_tasks(st.session_state.tasks)
                elif current_task.status == "completed":
                    st.session_state.current_launch_index += 1
                    save_tasks(st.session_state.tasks)
                # If running, wait for it to complete (in real implementation this would check agent status)
            else:
                st.session_state.current_launch_index += 1
        else:
            st.session_state.launch_running = False
            st.session_state.current_launch_index = 0
            st.success("✅ Launch queue completed!")
    
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
            col_task, col_add = st.columns([4, 1])
            with col_task:
                st.markdown(f"- {task.title}")
            with col_add:
                if st.button("➕ Queue", key=f"pending_queue_{task.id}"):
                    if task.id not in st.session_state.launch_queue:
                        st.session_state.launch_queue.append(task.id)
                        st.success("Added!")
                        st.rerun()
                    else:
                        st.warning("Already in queue!")
    
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
                # Check if user can still make requests
                if st.session_state.user_request_count >= 1:
                    st.error("🚫 Sie haben bereits Ihre Anfrage genutzt / You have already used your request")
                elif selected_task and selected_agent:
                    # Count this request
                    st.session_state.user_request_count += 1
                    
                    # Collect user data
                    if not st.session_state.user_collected:
                        request_data = {
                            "type": "task_execution",
                            "agent_used": selected_agent.name,
                            "task_title": selected_task.title,
                            "task_description": selected_task.description[:100],
                            "timestamp": datetime.now().isoformat()
                        }
                        collect_user_data(request_data)
                        st.session_state.user_collected = True
                        st.info("ℹ️ Ihre Daten wurden zur Optimierung gesammelt / Your data has been collected for optimization")
                    
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
        
        # LIVE PROGRESS INDICATOR HEADER
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #161b22 0%, #21262d 100%); 
                    border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div class="spinner"></div>
                    <div>
                        <div style="font-weight: 600; color: #c9d1d9; font-size: 16px;">
                            {selected_agent.name} is working
                        </div>
                        <div style="color: #8b949e; font-size: 13px;">
                            Task: {selected_task.title}
                        </div>
                    </div>
                </div>
                <div class="live-indicator">
                    <div class="live-dot"></div>
                    <span>LIVE</span>
                </div>
            </div>
            
            <!-- Animated Progress Bar -->
            <div style="background: #21262d; border-radius: 4px; height: 8px; overflow: hidden; margin-bottom: 12px;">
                <div class="progress-bar-animated" style="width: 100%;"></div>
            </div>
            
            <!-- Progress Steps -->
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <div class="step-indicator step-active">
                    <span style="color: #3fb950;">●</span>
                    <span style="color: #c9d1d9; font-size: 12px;">Analyzing</span>
                </div>
                <div class="step-indicator">
                    <span style="color: #8b949e;">○</span>
                    <span style="color: #8b949e; font-size: 12px;">Planning</span>
                </div>
                <div class="step-indicator">
                    <span style="color: #8b949e;">○</span>
                    <span style="color: #8b949e; font-size: 12px;">Coding</span>
                </div>
                <div class="step-indicator">
                    <span style="color: #8b949e;">○</span>
                    <span style="color: #8b949e; font-size: 12px;">Testing</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ETA Counter
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="eta-box">
                <div class="eta-value" id="elapsed-time">00:00</div>
                <div class="eta-label">Elapsed</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="eta-box">
                <div class="eta-value">~2m</div>
                <div class="eta-label">Estimated</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="eta-box">
                <div class="eta-value" style="color: #3fb950;">$0.00</div>
                <div class="eta-label">Cost So Far</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
        
        if LOCAL_MODE:
            # REAL AGENT EXECUTION with Live Progress
            import subprocess
            import threading
            import queue
            
            # Setup for real execution
            log_queue = queue.Queue()
            start_time = time.time()
            
            def run_real_agent():
                """Run the actual ClawWork agent"""
                try:
                    # Prepare environment with correct Python paths
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    pythonpath = f"{clawwork_path};{clawwork_path / 'livebench'};{clawwork_path / 'livebench' / 'agent'}"
                    env['PYTHONPATH'] = pythonpath
                    
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
                        cwd=str(BASE_DIR)
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
            
            # Live Output with Progress
            output_container = st.container()
            with output_container:
                st.markdown("### 🖥️ Live Console Output")
                
                # Progress metrics
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    token_placeholder = st.empty()
                with metrics_col2:
                    step_placeholder = st.empty()
                
                output_placeholder = st.empty()
                
                logs = []
                token_count = 0
                step = "Initializing"
                
                while True:
                    try:
                        line = log_queue.get(timeout=0.1)
                        if line == "__AGENT_FINISHED__":
                            break
                        
                        logs.append(line)
                        
                        # Parse progress from logs
                        if "token" in line.lower():
                            token_count += random.randint(50, 200)
                        if "iteration" in line.lower():
                            step = "Processing"
                        if "completed" in line.lower():
                            step = "Finalizing"
                        
                        # Update metrics
                        elapsed = int(time.time() - start_time)
                        token_placeholder.metric("Tokens Used", f"{token_count:,}")
                        step_placeholder.metric("Current Step", step)
                        
                        # Update display (last 30 lines)
                        output_placeholder.code("\n".join(logs[-30:]), language="bash")
                        
                    except queue.Empty:
                        # Update elapsed time even when no new logs
                        elapsed = int(time.time() - start_time)
                        mins = elapsed // 60
                        secs = elapsed % 60
                        
                        if not agent_thread.is_alive() and log_queue.empty():
                            break
                        continue
                
                agent_thread.join()
            
            # Mark complete
            selected_task.status = "completed"
            save_tasks(st.session_state.tasks)
            
            st.success("✅ Task completed successfully!")
            st.session_state.execution_running = True
            
            if st.button("📋 Back to Tasks"):
                st.session_state.page = "tasks"
                st.rerun()
        
        else:
            # SIMULATION MODE with Live Progress
            import random
            
            # Simulierte Schritte mit Fortschritt
            steps = [
                ("🔍", "Analyzing task requirements...", 10),
                ("📋", "Creating implementation plan...", 25),
                ("⚙️", "Setting up environment...", 40),
                ("💻", "Writing code...", 60),
                ("🧪", "Running tests...", 80),
                ("✅", "Finalizing and reviewing...", 95),
            ]
            
            output_container = st.container()
            with output_container:
                st.markdown("### 🖥️ Simulated Execution")
                
                # Live metrics
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    token_placeholder = st.empty()
                with metrics_col2:
                    step_placeholder = st.empty()
                
                log_placeholder = st.empty()
                
                logs = []
                token_count = 0
                start_time = time.time()
                
                for icon, step_text, target_progress in steps:
                    # Update step
                    step_placeholder.metric("Current Step", f"{icon} {step_text}")
                    
                    # Simulate progress within step
                    for progress in range(target_progress - 15, target_progress + 1, 5):
                        # Update tokens
                        token_count += random.randint(100, 500)
                        token_placeholder.metric("Tokens Used", f"{token_count:,}")
                        
                        # Add log entry
                        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {step_text} ({progress}%)")
                        log_placeholder.code("\n".join(logs[-10:]), language="bash")
                        
                        time.sleep(0.3)
                
                # Final
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Task completed!")
                log_placeholder.code("\n".join(logs[-10:]), language="bash")
            
            # Payment simulation
            payment = random.randint(20, 60)
            cost = random.randint(3, 10)
            
            # Mark complete
            selected_task.status = "completed"
            selected_agent.balance += payment - cost
            save_tasks(st.session_state.tasks)
            save_agents(st.session_state.agents)
            
            st.success(f"✅ Task completed! Earned ${payment}, Cost ${cost}, Profit ${payment-cost}")
            st.session_state.execution_running = True 
            
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

# ==================== MONITOR ====================
elif st.session_state.page == 'monitor':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    st.header("🖥️ Monitoring Terminal")
    st.caption("Real-time visual monitoring of all agent activities and task progress")
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        auto_refresh = st.toggle("🔄 Auto Refresh", value=True, key="monitor_auto_refresh")
    with col2:
        refresh_interval = st.select_slider("Interval", options=[1, 2, 5, 10], value=2, 
                                           format_func=lambda x: f"{x}s", key="refresh_interval")
    with col3:
        if st.button("📊 Export Report"):
            st.info("Report export feature coming soon!")
    
    st.markdown("<hr style='border-color: #21262d; margin: 16px 0;'>", unsafe_allow_html=True)
    
    # Summary Stats Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_agents = len(st.session_state.agents)
    running_agents = len([a for a in st.session_state.agents if a.status == "running"])
    idle_agents = len([a for a in st.session_state.agents if a.status == "idle"])
    pending_tasks = len([t for t in st.session_state.tasks if t.status == "pending"])
    running_tasks = len([t for t in st.session_state.tasks if t.status == "running"])
    completed_tasks = len([t for t in st.session_state.tasks if t.status == "completed"])
    total_balance = sum(a.balance for a in st.session_state.agents)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 3px solid #3fb950;">
            <div class="metric-value" style="font-size: 24px;">{running_agents}/{total_agents}</div>
            <div class="metric-label">Active Agents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 3px solid #f78166;">
            <div class="metric-value" style="font-size: 24px;">{running_tasks}</div>
            <div class="metric-label">Running Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 3px solid #58a6ff;">
            <div class="metric-value" style="font-size: 24px;">{completed_tasks}</div>
            <div class="metric-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 3px solid #a371f7;">
            <div class="metric-value" style="font-size: 24px;">${total_balance:.0f}</div>
            <div class="metric-label">Total Balance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        efficiency = (completed_tasks / (completed_tasks + pending_tasks) * 100) if (completed_tasks + pending_tasks) > 0 else 0
        st.markdown(f"""
        <div class="metric-box" style="border-left: 3px solid #3fb950;">
            <div class="metric-value" style="font-size: 24px;">{efficiency:.0f}%</div>
            <div class="metric-label">Efficiency</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Main monitoring content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Task Progress Overview")
        
        if not st.session_state.tasks:
            st.info("No tasks available. Create tasks to see progress monitoring.")
        else:
            for task in st.session_state.tasks[:5]:  # Show up to 5 tasks
                # Determine progress and color based on status
                if task.status == "completed":
                    progress = 100
                    progress_color = "#3fb950"
                    status_icon = "✅"
                elif task.status == "running":
                    # Simulate progress for running tasks
                    import random
                    progress = random.randint(30, 85)
                    progress_color = "#f78166"
                    status_icon = "🔄"
                else:  # pending
                    progress = 0
                    progress_color = "#8b949e"
                    status_icon = "⏳"
                
                # Find assigned agent
                assigned_agent_name = "Unassigned"
                if task.assigned_agent:
                    agent = next((a for a in st.session_state.agents if a.id == task.assigned_agent), None)
                    if agent:
                        assigned_agent_name = f"{agent.avatar} {agent.name}"
                
                st.markdown(f"""
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="font-weight: 600; color: #c9d1d9;">{status_icon} {task.title}</div>
                        <div style="font-size: 12px; color: #8b949e;">{assigned_agent_name}</div>
                    </div>
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 8px;">{task.description[:60]}{'...' if len(task.description) > 60 else ''}</div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="flex: 1; background: #21262d; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="width: {progress}%; height: 100%; background: {progress_color}; border-radius: 4px; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="font-size: 12px; color: {progress_color}; font-weight: 500; min-width: 35px;">{progress}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_right:
        st.subheader("🤖 Agent Status")
        
        for agent in st.session_state.agents:
            if agent.status == "running":
                status_color = "#f78166"
                pulse_animation = "animation: pulse 2s infinite;"
            elif agent.status == "idle":
                status_color = "#3fb950"
                pulse_animation = ""
            else:
                status_color = "#8b949e"
                pulse_animation = ""
            
            st.markdown(f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="font-size: 24px;">{agent.avatar}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: #c9d1d9;">{agent.name}</div>
                        <div style="font-size: 11px; color: #8b949e;">{agent.role}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: #8b949e;">${agent.balance}</div>
                        <div style="display: flex; align-items: center; gap: 4px; margin-top: 2px;">
                            <span style="width: 8px; height: 8px; background: {status_color}; border-radius: 50%; {pulse_animation}"></span>
                            <span style="font-size: 10px; color: {status_color}; text-transform: uppercase;">{agent.status}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # System Health
        st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
        st.subheader("⚡ System Health")
        
        import random
        cpu_usage = random.randint(20, 60) if running_agents > 0 else random.randint(5, 15)
        memory_usage = random.randint(30, 70) if running_agents > 0 else random.randint(20, 40)
        
        cpu_color = "#3fb950" if cpu_usage < 70 else "#f78166" if cpu_usage < 90 else "#f85149"
        mem_color = "#3fb950" if memory_usage < 70 else "#f78166" if memory_usage < 90 else "#f85149"
        
        st.markdown(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px;">
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8b949e; margin-bottom: 4px;">
                    <span>CPU Usage</span>
                    <span>{cpu_usage}%</span>
                </div>
                <div style="background: #21262d; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="width: {cpu_usage}%; height: 100%; background: {cpu_color}; border-radius: 3px;"></div>
                </div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8b949e; margin-bottom: 4px;">
                    <span>Memory</span>
                    <span>{memory_usage}%</span>
                </div>
                <div style="background: #21262d; height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="width: {memory_usage}%; height: 100%; background: {mem_color}; border-radius: 3px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Live Console Output Section
    st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
    st.subheader("📜 Live Activity Log")
    
    # Generate simulated log entries based on current state
    import time
    current_time = datetime.now().strftime("%H:%M:%S")
    
    log_entries = [
        ("INFO", f"[{current_time}] Monitoring terminal initialized"),
        ("INFO", f"[{current_time}] Connected to {total_agents} agents"),
    ]
    
    if running_agents > 0:
        log_entries.append(("ACTIVE", f"[{current_time}] {running_agents} agent(s) currently working"))
    
    for task in st.session_state.tasks:
        if task.status == "running":
            log_entries.append(("TASK", f"[{current_time}] Task '{task.title}' is in progress"))
        elif task.status == "completed":
            log_entries.append(("SUCCESS", f"[{current_time}] Task '{task.title}' completed successfully"))
    
    # Display logs in terminal style
    log_html = '<div class="terminal" style="max-height: 300px;">'
    for level, message in log_entries:
        if level == "INFO":
            color = "#8b949e"
        elif level == "ACTIVE":
            color = "#58a6ff"
        elif level == "TASK":
            color = "#f78166"
        elif level == "SUCCESS":
            color = "#3fb950"
        else:
            color = "#c9d1d9"
        
        log_html += f'<div class="terminal-line" style="color: {color};">{message}</div>'
    
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage
        st.rerun()

# ==================== KUBERNETES / BOTNET ====================
elif st.session_state.page == 'kubernetes':
    st.markdown("<div style='padding: 24px 0;'></div>", unsafe_allow_html=True)
    
    st.header("☸️ Kubernetes Botnet Orchestrator")
    st.caption("Deploy and manage distributed agent botnets on Kubernetes")
    
    # Tabs for different sections
    tab_botnets, tab_deployments, tab_agents = st.tabs(["🕸️ Botnets", "📦 Deployments", "🤖 Agent Pool"])
    
    with tab_botnets:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Botnet Clusters")
        with col2:
            if st.button("➕ Create Botnet", type="primary", use_container_width=True):
                st.session_state.show_new_botnet = True
        
        # Create Botnet Form
        if st.session_state.get('show_new_botnet', False):
            with st.expander("Create New Botnet", expanded=True):
                with st.form("new_botnet"):
                    botnet_name = st.text_input("Botnet Name", placeholder="e.g., DataProcessingSwarm")
                    botnet_desc = st.text_area("Description", placeholder="Purpose of this botnet cluster...")
                    
                    # Select agents for this botnet
                    available_agents = [a for a in st.session_state.agents if a.status == "idle"]
                    selected_agents = st.multiselect(
                        "Assign Agents to Botnet",
                        options=[f"{a.avatar} {a.name}" for a in available_agents],
                        help="Select agents to include in this botnet"
                    )
                    
                    col_create, col_cancel = st.columns([1, 5])
                    with col_create:
                        if st.form_submit_button("Create", type="primary"):
                            if botnet_name and selected_agents:
                                new_botnet = Botnet(
                                    id=f"botnet-{uuid.uuid4().hex[:8]}",
                                    name=botnet_name,
                                    description=botnet_desc,
                                    agent_ids=[a.id for a in available_agents if f"{a.avatar} {a.name}" in selected_agents],
                                    status="idle",
                                    created_at=datetime.now().isoformat(),
                                    deployment_count=0
                                )
                                st.session_state.botnets.append(new_botnet)
                                st.session_state.show_new_botnet = False
                                st.success(f"Botnet '{botnet_name}' created with {len(selected_agents)} agents!")
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_new_botnet = False
                            st.rerun()
        
        # Display Botnets
        if not st.session_state.botnets:
            st.info("No botnets created yet. Create a botnet to orchestrate multiple agents.")
        else:
            for botnet in st.session_state.botnets:
                status_colors = {
                    "idle": "#8b949e",
                    "deploying": "#f78166",
                    "active": "#3fb950",
                    "stopped": "#f85149"
                }
                status_color = status_colors.get(botnet.status, "#8b949e")
                
                # Get assigned agents
                assigned_agents = [a for a in st.session_state.agents if a.id in botnet.agent_ids]
                agent_count = len(assigned_agents)
                
                with st.expander(f"🕸️ {botnet.name} ({agent_count} agents)"):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**Description:** {botnet.description}")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>● {botnet.status.upper()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Created:** {botnet.created_at[:19]}")
                        st.markdown(f"**Deployments:** {botnet.deployment_count}")
                        
                        st.markdown("**Assigned Agents:**")
                        for agent in assigned_agents:
                            st.markdown(f"- {agent.avatar} {agent.name} ({agent.role})")
                    
                    with col_actions:
                        if botnet.status == "idle":
                            if st.button("🚀 Deploy", key=f"deploy_{botnet.id}", use_container_width=True):
                                botnet.status = "deploying"
                                st.rerun()
                        elif botnet.status == "active":
                            if st.button("⏹️ Stop", key=f"stop_{botnet.id}", use_container_width=True):
                                botnet.status = "stopped"
                                st.rerun()
                            if st.button("🔄 Restart", key=f"restart_{botnet.id}", use_container_width=True):
                                botnet.status = "deploying"
                                st.rerun()
                        elif botnet.status == "stopped":
                            if st.button("▶️ Start", key=f"start_{botnet.id}", use_container_width=True):
                                botnet.status = "active"
                                st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_botnet_{botnet.id}", use_container_width=True):
                            st.session_state.botnets.remove(botnet)
                            st.rerun()
    
    with tab_deployments:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Kubernetes Deployments")
        with col2:
            if st.button("➕ New Deployment", type="primary", use_container_width=True):
                st.session_state.show_new_deployment = True
        
        # Create Deployment Form
        if st.session_state.get('show_new_deployment', False):
            with st.expander("Create K8s Deployment", expanded=True):
                with st.form("new_k8s_deployment"):
                    dep_name = st.text_input("Deployment Name", placeholder="e.g., crawler-deployment")
                    dep_namespace = st.text_input("Namespace", value="default")
                    dep_image = st.text_input("Container Image", placeholder="e.g., myapp:latest")
                    dep_replicas = st.number_input("Replicas", min_value=1, max_value=100, value=3)
                    
                    # Select botnet to deploy to
                    botnet_options = [f"🕸️ {b.name}" for b in st.session_state.botnets if b.status in ["idle", "active"]]
                    if botnet_options:
                        selected_botnet = st.selectbox("Deploy to Botnet", botnet_options)
                    else:
                        st.warning("No active botnets available. Create a botnet first.")
                        selected_botnet = None
                    
                    col_create, col_cancel = st.columns([1, 5])
                    with col_create:
                        if st.form_submit_button("Deploy", type="primary"):
                            if dep_name and selected_botnet:
                                botnet_name = selected_botnet.replace("🕸️ ", "")
                                botnet = next((b for b in st.session_state.botnets if b.name == botnet_name), None)
                                
                                new_dep = K8sDeployment(
                                    id=f"k8s-{uuid.uuid4().hex[:8]}",
                                    name=dep_name,
                                    namespace=dep_namespace,
                                    replicas=dep_replicas,
                                    image=dep_image,
                                    status="pending",
                                    agent_id=botnet.agent_ids[0] if botnet and botnet.agent_ids else "",
                                    created_at=datetime.now().isoformat(),
                                    botnet_id=botnet.id if botnet else None
                                )
                                st.session_state.k8s_deployments.append(new_dep)
                                if botnet:
                                    botnet.deployment_count += 1
                                st.session_state.show_new_deployment = False
                                st.success(f"Deployment '{dep_name}' created!")
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state.show_new_deployment = False
                            st.rerun()
        
        # Display Deployments
        if not st.session_state.k8s_deployments:
            st.info("No Kubernetes deployments yet.")
        else:
            for dep in st.session_state.k8s_deployments:
                status_colors = {
                    "pending": "#8b949e",
                    "deploying": "#f78166",
                    "running": "#3fb950",
                    "failed": "#f85149"
                }
                status_color = status_colors.get(dep.status, "#8b949e")
                
                with st.expander(f"📦 {dep.name} ({dep.namespace})"):
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**Image:** `{dep.image}`")
                        st.markdown(f"**Replicas:** {dep.replicas}")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>● {dep.status.upper()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Created:** {dep.created_at[:19]}")
                        
                        # Show assigned botnet
                        if dep.botnet_id:
                            botnet = next((b for b in st.session_state.botnets if b.id == dep.botnet_id), None)
                            if botnet:
                                st.markdown(f"**Managed by Botnet:** {botnet.name}")
                    
                    with col_actions:
                        if dep.status == "pending":
                            if st.button("▶️ Start", key=f"start_dep_{dep.id}", use_container_width=True):
                                dep.status = "deploying"
                                st.rerun()
                        elif dep.status == "failed":
                            if st.button("🔄 Retry", key=f"retry_dep_{dep.id}", use_container_width=True):
                                dep.status = "deploying"
                                st.rerun()
                        elif dep.status == "running":
                            if st.button("⏹️ Stop", key=f"stop_dep_{dep.id}", use_container_width=True):
                                dep.status = "pending"
                                st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_dep_{dep.id}", use_container_width=True):
                            st.session_state.k8s_deployments.remove(dep)
                            st.rerun()
                        
                        # Generate K8s YAML
                        if st.button("📄 View YAML", key=f"yaml_{dep.id}", use_container_width=True):
                            yaml_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {dep.name}
  namespace: {dep.namespace}
spec:
  replicas: {dep.replicas}
  selector:
    matchLabels:
      app: {dep.name}
  template:
    metadata:
      labels:
        app: {dep.name}
    spec:
      containers:
      - name: app
        image: {dep.image}
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""
                            st.code(yaml_content, language="yaml")
    
    with tab_agents:
        st.subheader("Available Agent Pool")
        
        # Show agent pool stats
        idle_agents = [a for a in st.session_state.agents if a.status == "idle"]
        busy_agents = [a for a in st.session_state.agents if a.status in ["running", "busy"]]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Idle Agents", len(idle_agents))
        with col2:
            st.metric("Busy Agents", len(busy_agents))
        with col3:
            st.metric("Total Agents", len(st.session_state.agents))
        
        # Quick actions for agents
        st.markdown("<div style='padding: 16px 0;'></div>", unsafe_allow_html=True)
        
        for agent in st.session_state.agents:
            col_agent, col_status, col_action = st.columns([3, 1, 1])
            
            with col_agent:
                status_dot = "🟢" if agent.status == "idle" else "🟠" if agent.status == "running" else "⚪"
                st.markdown(f"{agent.avatar} **{agent.name}** ({agent.role})")
            
            with col_status:
                st.markdown(f"{status_dot} {agent.status.upper()}")
            
            with col_action:
                # Check if agent is in any botnet
                in_botnet = any(agent.id in b.agent_ids for b in st.session_state.botnets)
                if in_botnet:
                    st.markdown("✅ In Botnet")
                else:
                    if st.button("➕ Assign", key=f"assign_k8s_{agent.id}"):
                        st.session_state.selected_agent_for_botnet = agent
                        st.rerun()

# Footer
st.markdown("<div style='padding: 32px 0;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top: 1px solid #21262d; padding: 16px 0; text-align: center; color: #8b949e; font-size: 12px;">
    🦞 KimiClaw v3.0.0-multiagent | Multi-Agent IDE | 
    <a href="https://github.com/loslos321-lab/openklaw_5.1-beta" style="color: #58a6ff;">GitHub</a>
</div>
""", unsafe_allow_html=True)

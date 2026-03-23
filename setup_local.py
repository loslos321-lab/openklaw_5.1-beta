#!/usr/bin/env python3
"""
KimiClaw Local Setup - Full Power Mode
Installiert alles für lokale Nutzung mit echten API Calls
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show output"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Done")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("="*60)
    print("🦞 KimiClaw Local Setup - Full Power Mode")
    print("="*60)
    print("\nThis will set up KimiClaw for local use with:")
    print("  ✅ Real API calls to Kimi/SiliconFlow")
    print("  ✅ Full ClawWork integration")
    print("  ✅ No timeouts or limitations")
    print("  ✅ Persistent data storage")
    print()
    
    base_dir = Path(__file__).parent
    
    # Step 1: Check Python version
    print(f"\n📍 Python version: {sys.version}")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required!")
        return 1
    print("✅ Python version OK")
    
    # Step 2: Create virtual environment
    venv_path = base_dir / "venv"
    if not venv_path.exists():
        print("\n📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment exists")
    
    # Step 3: Get Python path in venv
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    # Step 4: Upgrade pip
    print("\n⬆️  Upgrading pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Step 5: Install requirements
    print("\n📥 Installing requirements...")
    req_file = base_dir / "requirements_local.txt"
    if req_file.exists():
        subprocess.run([str(pip_path), "install", "-r", str(req_file)], check=True)
    else:
        # Fallback to standard requirements
        subprocess.run([str(pip_path), "install", "-r", str(base_dir / "requirements.txt")], check=True)
    
    # Step 6: Additional dependencies for full ClawWork
    print("\n📥 Installing ClawWork dependencies...")
    additional_deps = [
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "langchain-mcp-adapters>=0.1.0",
        "langgraph>=0.2.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "websockets>=12.0",
        "httpx>=0.25.0",
        "e2b-code-interpreter>=1.0.0",
        "tavily-python>=0.3.0",
        "python-docx>=1.0.0",
        "reportlab>=4.0.0",
        "openpyxl>=3.1.0",
    ]
    
    for dep in additional_deps:
        print(f"  Installing {dep}...")
        subprocess.run([str(pip_path), "install", dep], capture_output=True)
    
    # Step 7: Check .env file
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("\n⚠️  Creating .env from template...")
        with open(env_example) as f:
            content = f.read()
        with open(env_file, "w") as f:
            f.write(content)
        print("✅ Created .env file")
    
    # Step 8: Create launcher scripts
    print("\n📝 Creating launcher scripts...")
    
    # Windows launcher
    bat_content = f'''@echo off
cd /d "{base_dir}"
call venv\\Scripts\\activate.bat
set PYTHONIOENCODING=utf-8
streamlit run interface\\app.py --server.port 8501
echo.
echo KimiClaw stopped.
pause
'''
    with open(base_dir / "start_local.bat", "w") as f:
        f.write(bat_content)
    
    # PowerShell launcher
    ps_content = f'''$env:PYTHONIOENCODING = "utf-8"
Set-Location "{base_dir}"
& .\\venv\\Scripts\\Activate.ps1
streamlit run interface\\app.py --server.port 8501
'''
    with open(base_dir / "start_local.ps1", "w") as f:
        f.write(ps_content)
    
    print("✅ Created start_local.bat and start_local.ps1")
    
    # Step 9: Success message
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\n🚀 Next steps:")
    print("1. Edit .env file and add your API key:")
    print(f"   notepad {base_dir}\\.env")
    print("\n2. Start KimiClaw:")
    print("   .\\start_local.bat")
    print("   or")
    print("   .\\start_local.ps1")
    print("\n3. Open browser:")
    print("   http://localhost:8501")
    print("\n💡 Features unlocked:")
    print("   ✅ Real API calls")
    print("   ✅ No timeouts")
    print("   ✅ Full ClawWork integration")
    print("   ✅ Code sandbox execution")
    print("   ✅ Web search")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

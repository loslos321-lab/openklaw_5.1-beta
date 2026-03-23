#!/usr/bin/env python3
"""
Test script to verify KimiClaw Master Coder setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    errors = []
    
    # Test standard library
    try:
        import json, asyncio, argparse
        print("  [OK] Standard library")
    except ImportError as e:
        errors.append(f"Standard library: {e}")
    
    # Test ClawWork path - add both root and livebench to path
    clawwork_path = Path("c:/Users/Student/ClawWork")
    livebench_path = clawwork_path / "livebench"
    
    if str(clawwork_path) not in sys.path:
        sys.path.insert(0, str(clawwork_path))
    if str(livebench_path) not in sys.path:
        sys.path.insert(0, str(livebench_path))
    
    # Also add agent path specifically
    agent_path = livebench_path / "agent"
    if str(agent_path) not in sys.path:
        sys.path.insert(0, str(agent_path))
    
    # Test ClawWork imports
    try:
        # Change to ClawWork directory for imports
        original_dir = os.getcwd()
        os.chdir(str(clawwork_path))
        from livebench.agent.live_agent import LiveAgent
        os.chdir(original_dir)
        print("  [OK] LiveAgent")
    except ImportError as e:
        errors.append(f"LiveAgent: {e}")
    
    try:
        from livebench.work.task_manager import TaskManager
        print("  [OK] TaskManager")
    except ImportError as e:
        errors.append(f"TaskManager: {e}")
    
    try:
        from livebench.agent.economic_tracker import EconomicTracker
        print("  [OK] EconomicTracker")
    except ImportError as e:
        errors.append(f"EconomicTracker: {e}")
    
    # Test external dependencies
    try:
        import dotenv
        print("  [OK] python-dotenv")
    except ImportError as e:
        errors.append(f"python-dotenv: {e}")
    
    try:
        import langchain
        print("  [OK] langchain")
    except ImportError as e:
        errors.append(f"langchain: {e}")
    
    if errors:
        print("\n[FAIL] Import errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    
    print("\n[OK] All imports successful!")
    return True


def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check directories
    dirs = ["./data", "./memory", "./work", "./sandbox", "./skills"]
    for d in dirs:
        path = Path(d)
        if not path.exists():
            print(f"  Creating {d}...")
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"  [OK] {d}")
    
    # Check config files
    configs = ["master_coder_config.json", ".env", "requirements.txt"]
    for cfg in configs:
        path = Path(cfg)
        if path.exists():
            print(f"  [OK] {cfg}")
        else:
            print(f"  [WARN] {cfg} not found")
    
    print("\n[OK] Environment setup complete!")
    return True


def test_mcp_server():
    """Test MCP server connection"""
    print("\nTesting MCP server...")
    
    import urllib.request
    import urllib.error
    
    mcp_url = "http://127.0.0.1:64342/sse"
    
    try:
        req = urllib.request.Request(mcp_url, method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"  [OK] MCP server responding at {mcp_url}")
            print(f"  Status: {response.status}")
            return True
    except urllib.error.URLError as e:
        print(f"  [WARN] MCP server not responding: {e}")
        print(f"  URL: {mcp_url}")
        print("  The server may need to be started manually")
        return False
    except Exception as e:
        print(f"  [WARN] Error connecting: {e}")
        return False


def test_clawwork_integration():
    """Test ClawWork integration"""
    print("\nTesting ClawWork integration...")
    
    clawwork_path = Path("c:/Users/Student/ClawWork")
    
    if not clawwork_path.exists():
        print(f"  [FAIL] ClawWork not found at {clawwork_path}")
        return False
    
    print(f"  [OK] ClawWork found at {clawwork_path}")
    
    # Check key directories
    key_dirs = [
        "livebench/agent",
        "livebench/tools",
        "livebench/work",
        "eval/meta_prompts"
    ]
    
    for d in key_dirs:
        path = clawwork_path / d
        if path.exists():
            print(f"  [OK] {d}")
        else:
            print(f"  [WARN] {d} not found")
    
    print("\n[OK] ClawWork integration verified!")
    return True


def main():
    print("="*60)
    print("KimiClaw Master Coder - Setup Test")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("MCP Server", test_mcp_server()))
    results.append(("ClawWork", test_clawwork_integration()))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("="*60)
    if all_passed:
        print("All tests passed! Ready to code.")
    else:
        print("Some tests failed. Check the output above.")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

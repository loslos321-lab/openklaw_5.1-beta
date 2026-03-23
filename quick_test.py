#!/usr/bin/env python3
"""Quick test for KimiClaw Master Coder"""

import os
import sys
import asyncio
from pathlib import Path

# Store base directory
base_dir = Path.cwd()

# Add ClawWork to path
CLAWWORK_PATH = Path("c:/Users/Student/ClawWork")
for p in [str(CLAWWORK_PATH), str(CLAWWORK_PATH / "livebench"), str(CLAWWORK_PATH / "livebench" / "agent")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Change to ClawWork for imports
os.chdir(str(CLAWWORK_PATH))

from dotenv import load_dotenv
load_dotenv(str(base_dir / ".env"))

from livebench.agent.live_agent import LiveAgent

async def test():
    print("="*60)
    print("KimiClaw Master Coder - Quick Test")
    print("="*60)
    
    agent = LiveAgent(
        signature="kimiclaw-test",
        basemodel="kimi-k2-0725",
        initial_balance=100.0,
        input_token_price=0.0025,
        output_token_price=0.01,
        data_path=str(base_dir / "data"),
        task_source_type="inline",
        inline_tasks=[{
            "task_id": "test-task-1",
            "sector": "Technology",
            "occupation": "Software Developer",
            "prompt": "Write a simple Python function that adds two numbers and returns the result.",
            "task_description": "Simple addition function",
            "estimated_hours": 1,
            "reference_files": []
        }],
        use_llm_evaluation=True,
        max_steps=5
    )
    
    print("\nInitializing agent...")
    await agent.initialize()
    print("Agent initialized successfully!")
    
    print("\nRunning test task...")
    from datetime import datetime
    result = await agent.run_daily_session(datetime.now().strftime("%Y-%m-%d"))
    print(f"\nResult: {result}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test())

#!/usr/bin/env python3
"""
KimiClaw Master Coder - All-Round Coding Agent Runner
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add ClawWork to path BEFORE any imports
CLAWWORK_PATH = Path("c:/Users/Student/ClawWork")
CLAWWORK_LIVEBENCH = CLAWWORK_PATH / "livebench"
CLAWWORK_AGENT = CLAWWORK_LIVEBENCH / "agent"

for p in [str(CLAWWORK_PATH), str(CLAWWORK_LIVEBENCH), str(CLAWWORK_AGENT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Now change directory for imports
original_dir = os.getcwd()
os.chdir(str(CLAWWORK_PATH))

# Import after path setup
from dotenv import load_dotenv
from livebench.agent.live_agent import LiveAgent
from livebench.work.task_manager import TaskManager
from livebench.agent.economic_tracker import EconomicTracker

# Load environment variables
os.chdir(original_dir)  # Back to kimiclaw for .env
load_dotenv()
os.chdir(str(CLAWWORK_PATH))  # Back to ClawWork for imports


class KimiClawMasterCoder:
    """Master Coder Agent with enhanced capabilities"""
    
    def __init__(self, config_path: str = "master_coder_config.json", base_dir: str = None):
        """Initialize the master coder agent"""
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.config = self._load_config(config_path)
        self.agent_config = self.config.get("livebench", {})
        self.agent = None
        self._setup_environment()
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        # Use absolute path from base directory
        config_full_path = self.base_dir / config_path
        try:
            with open(config_full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_full_path}")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "livebench": {
                "agents": [{
                    "signature": "kimiclaw-master-coder",
                    "basemodel": "gpt-4o",
                    "enabled": True,
                    "tasks_per_day": 3
                }],
                "task_source": {
                    "type": "inline",
                    "tasks": [
                        {
                            "task_id": "coding-task-1",
                            "sector": "Technology",
                            "occupation": "Software Developer",
                            "prompt": "Create a Python function that reads a CSV file and calculates statistics.",
                            "task_description": "CSV statistics calculator",
                            "estimated_hours": 2,
                            "reference_files": []
                        }
                    ]
                },
                "economic": {"initial_balance": 100.0},
                "agent_params": {
                    "max_steps": 50,
                    "max_retries": 5
                }
            }
        }
    
    def _setup_environment(self):
        """Setup environment variables and paths"""
        paths = [self.base_dir / "data", self.base_dir / "memory", 
                 self.base_dir / "work", self.base_dir / "sandbox"]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the agent"""
        agent_cfg = self.agent_config.get("agents", [{}])[0]
        econ_cfg = self.agent_config.get("economic", {})
        params = self.agent_config.get("agent_params", {})
        
        print("Initializing KimiClaw Master Coder...")
        print(f"   Signature: {agent_cfg.get('signature')}")
        print(f"   Model: {agent_cfg.get('basemodel')}")
        print(f"   Initial Balance: ${econ_cfg.get('initial_balance', 100.0)}")
        
        # Get task source configuration
        task_source = self.agent_config.get("task_source", {})
        task_source_type = task_source.get("type", "inline")
        inline_tasks = task_source.get("tasks", []) if task_source_type == "inline" else None
        
        # Switch to ClawWork for initialization
        os.chdir(str(CLAWWORK_PATH))
        
        self.agent = LiveAgent(
            signature=agent_cfg.get("signature", "kimiclaw-master-coder"),
            basemodel=agent_cfg.get("basemodel", "gpt-4o"),
            initial_balance=econ_cfg.get("initial_balance", 100.0),
            input_token_price=econ_cfg.get("token_pricing", {}).get("input_per_1m", 2.5) / 1000,
            output_token_price=econ_cfg.get("token_pricing", {}).get("output_per_1m", 10.0) / 1000,
            max_steps=params.get("max_steps", 50),
            max_retries=params.get("max_retries", 5),
            base_delay=params.get("base_delay", 1.0),
            api_timeout=params.get("api_timeout", 120.0),
            tasks_per_day=agent_cfg.get("tasks_per_day", 3),
            supports_multimodal=agent_cfg.get("supports_multimodal", True),
            data_path=str(self.base_dir / "data"),
            use_llm_evaluation=self.agent_config.get("evaluation", {}).get("use_llm_evaluation", True),
            meta_prompts_dir=str(CLAWWORK_PATH / "eval" / "meta_prompts"),
            task_source_type=task_source_type,
            inline_tasks=inline_tasks
        )
        
        await self.agent.initialize()
        print("Agent initialized successfully!")
    
    async def run_interactive(self):
        """Run in interactive mode"""
        print("\n" + "="*60)
        print("KimiClaw Master Coder - Interactive Mode")
        print("="*60)
        print("\nAvailable commands:")
        print("  work    - Complete a work task")
        print("  learn   - Learn something new")
        print("  status  - Check economic status")
        print("  quit    - Exit\n")
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == "quit":
                    print("Goodbye!")
                    break
                elif command == "status":
                    status = self.agent.economic_tracker.get_summary()
                    print(f"\nBalance: ${status.get('balance', 0):.2f}")
                    print(f"Status: {status.get('survival_status', 'unknown')}")
                elif command == "work":
                    today = datetime.now().strftime("%Y-%m-%d")
                    result = await self.agent.run_daily_session(today)
                    if result == "NO_TASKS_AVAILABLE":
                        print("No more tasks available")
                        break
                elif command == "learn":
                    topic = input("Topic to learn: ")
                    print(f"Learning about {topic}...")
                else:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def run_work_mode(self, days: int = 1):
        """Run in work mode"""
        print(f"\nStarting Work Mode ({days} days)\n")
        
        start_date = datetime.now()
        
        for day in range(days):
            date = (start_date.replace(day=start_date.day + day)).strftime("%Y-%m-%d")
            print(f"\nDay {day + 1}/{days}: {date}")
            print("-" * 40)
            
            result = await self.agent.run_daily_session(date)
            
            if result == "NO_TASKS_AVAILABLE":
                print("No more tasks available")
                break
            elif result == "ERROR":
                print("Error occurred, continuing...")
            
            if day < days - 1:
                await asyncio.sleep(2)
        
        print("\nWork mode completed!")
        self._print_summary()
    
    def _print_summary(self):
        """Print session summary"""
        if not self.agent:
            return
            
        summary = self.agent.economic_tracker.get_summary()
        print("\n" + "="*60)
        print("Session Summary")
        print("="*60)
        print(f"Final Balance: ${summary.get('balance', 0):.2f}")
        print(f"Net Worth: ${summary.get('net_worth', 0):.2f}")
        print(f"Total Costs: ${summary.get('total_costs', 0):.2f}")
        print(f"Total Income: ${summary.get('total_income', 0):.2f}")
        print(f"Status: {summary.get('survival_status', 'unknown')}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="KimiClaw Master Coder - All-Round Coding Agent"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="interactive",
        choices=["interactive", "work", "learn", "sandbox"],
        help="Run mode (default: interactive)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to run (for work mode)"
    )
    parser.add_argument(
        "--config",
        default="master_coder_config.json",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Store base directory before any chdir
    base_dir = Path.cwd()
    
    try:
        master_coder = KimiClawMasterCoder(config_path=args.config, base_dir=str(base_dir))
        asyncio.run(master_coder.initialize())
        
        if args.mode == "interactive":
            asyncio.run(master_coder.run_interactive())
        elif args.mode == "work":
            asyncio.run(master_coder.run_work_mode(days=args.days))
        else:
            print(f"Mode '{args.mode}' not yet implemented")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

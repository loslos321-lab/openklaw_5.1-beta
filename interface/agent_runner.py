"""
Agent Runner - Starts the actual ClawWork agent as subprocess
"""

import subprocess
import sys
import os
import threading
import queue
import time
from pathlib import Path

BASE_DIR = Path("c:/Users/Student/kimiclaw")
CLAWWORK_DIR = Path("c:/Users/Student/ClawWork")

class AgentRunner:
    """Runs the ClawWork agent in a subprocess"""
    
    def __init__(self):
        self.process = None
        self.log_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        
    def start(self, mode="work", days=1):
        """Start the agent subprocess"""
        if self.is_running:
            return False, "Agent already running"
        
        # Build command
        cmd = [
            sys.executable,
            str(BASE_DIR / "run_agent.py"),
            mode,
            "--days", str(days)
        ]
        
        # Environment with proper paths
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONPATH'] = f"{CLAWWORK_DIR};{CLAWWORK_DIR / 'livebench'};{CLAWWORK_DIR / 'livebench' / 'agent'}"
        
        try:
            # Start subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env,
                cwd=str(CLAWWORK_DIR)
            )
            
            self.is_running = True
            
            # Start log reader thread
            self.thread = threading.Thread(target=self._read_output)
            self.thread.daemon = True
            self.thread.start()
            
            return True, f"Agent started with PID {self.process.pid}"
            
        except Exception as e:
            return False, f"Failed to start agent: {str(e)}"
    
    def stop(self):
        """Stop the agent subprocess"""
        if not self.is_running or not self.process:
            return False, "Agent not running"
        
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            return True, "Agent stopped"
            
        except Exception as e:
            return False, f"Error stopping agent: {str(e)}"
    
    def _read_output(self):
        """Read output from subprocess"""
        while self.is_running and self.process:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.log_queue.put(line.strip())
                elif self.process.poll() is not None:
                    break
            except:
                break
        
        self.is_running = False
    
    def get_logs(self):
        """Get all pending logs"""
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return logs
    
    def check_status(self):
        """Check if process is still running"""
        if self.process:
            return self.process.poll() is None
        return False


# Global runner instance
_runner = None

def get_runner():
    """Get or create agent runner"""
    global _runner
    if _runner is None:
        _runner = AgentRunner()
    return _runner

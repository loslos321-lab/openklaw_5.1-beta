#!/usr/bin/env python3
"""Create a test task for KimiClaw"""

import sys
from pathlib import Path

# Add interface to path
sys.path.insert(0, str(Path(__file__).parent / "interface"))

from database import Database

db = Database()

test_task = {
    'task_id': 'test-task-003',
    'sector': 'Technology',
    'occupation': 'Test Developer',
    'title': 'Test Task - Hello World Function',
    'description': 'Ein einfacher Test um den Agenten zu prüfen',
    'prompt': '''Schreibe ein einfaches Python Programm mit folgenden Anforderungen:

1. Eine Funktion `greet(name)` die "Hello {name}!" zurückgibt
2. Eine Funktion `main()` die den Benutzer nach seinem Namen fragt und greet() aufruft
3. Docstrings für beide Funktionen
4. Ein einfacher Test mit assert
5. Falls __name__ == "__main__": Block

Speichere das Ergebnis in einer Datei namens "hello.py".''',
    'estimated_hours': 0.5,
    'max_payment': 25.0
}

try:
    db.add_task(test_task)
    print("[OK] Test-Task erfolgreich erstellt!")
    print(f"   Task ID: {test_task['task_id']}")
    print(f"   Titel: {test_task['title']}")
    print(f"   Sektor: {test_task['sector']}")
    print(f"   Max Payment: ${test_task['max_payment']}")
    print(f"\n[INFO] Aktuelle Anzahl Tasks: {len(db.get_all_tasks())}")
except Exception as e:
    print(f"[ERROR] Fehler: {e}")

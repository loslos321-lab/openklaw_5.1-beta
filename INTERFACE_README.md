# 🖥️ KimiClaw Web Interface

Eine benutzerfreundliche Web-Oberfläche zur Steuerung deines Code-Agenten.

## 🚀 Schnellstart

### Option 1: PowerShell (empfohlen)
```powershell
cd c:\Users\Student\kimiclaw
.\start_interface.ps1
```

### Option 2: Batch-Datei
```cmd
cd c:\Users\Student\kimiclaw
start_interface.bat
```

### Option 3: Manuell
```powershell
cd c:\Users\Student\kimiclaw
$env:PYTHONIOENCODING="utf-8"
python -m streamlit run interface\app.py
```

---

## 🌐 Interface öffnet automatisch:
- **Lokal:** http://localhost:8502
- **Netzwerk:** http://192.168.178.78:8502

---

## 📋 Funktionen

| Bereich | Beschreibung |
|---------|-------------|
| **🏠 Dashboard** | Übersicht mit Balance, Status, Quick-Actions |
| **▶️ Agent** | Agent starten/stoppen, Live-Logs |
| **📋 Tasks** | Aufgaben verwalten, neue hinzufügen |
| **💰 Economy** | Finanz-Übersicht, Transaktionen |
| **⚙️ Settings** | API Keys, Modell-Einstellungen |

---

## 💾 Datenbank

Das Interface verwendet **SQLite** (lokal):
- Datei: `data/kimiclaw.db`
- Keine externe Datenbank nötig
- Daten bleiben lokal gespeichert

---

## 🔧 Erste Schritte

1. **Interface starten**
   ```powershell
   .\start_interface.ps1
   ```

2. **Einstellungen öffnen**
   - Gehe zu "⚙️ Settings"
   - Trage deinen API Key ein
   - Speichern

3. **Agent starten**
   - Gehe zu "▶️ Agent"
   - Wähle Modus (Work/Interactive)
   - Klicke "START AGENT"

4. **Fortschritt verfolgen**
   - Live-Logs im Agent-Bereich
   - Tasks unter "📋 Tasks"

---

## 📂 Dateien

```
interface/
├── app.py           # Haupt-Anwendung
├── database.py      # SQLite Datenbank
start_interface.bat  # Windows Starter
start_interface.ps1  # PowerShell Starter
```

---

## 🎯 Features

- ✅ SQLite Datenbank (kein Setup nötig)
- ✅ Intuitive Web-Oberfläche
- ✅ Live-Log-Anzeige
- ✅ Task-Management
- ✅ Economy-Tracking
- ✅ Einstellungen per GUI

---

**Öffne jetzt:** http://localhost:8502

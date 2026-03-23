# 🦞 KimiClaw Master Coder

Ein KI-gestützter Code-Agent mit wirtschaftlichem Anreizsystem.

## 🚀 Schnellstart

### Lokale Installation
```bash
pip install -r requirements.txt
streamlit run interface/app.py
```

### Online
Die App läuft auf Streamlit Cloud: [Hier öffnen](https://kimiclaw.streamlit.app)

## 🎯 Features

- ✅ **Code-Generierung** in Python, JavaScript, und mehr
- ✅ **Wirtschaftssystem** - Agent verdient Geld für gute Arbeit
- ✅ **Task-Management** - Aufgaben erstellen und verwalten
- ✅ **Live-Monitoring** - Logs und Status in Echtzeit

## 🔧 Konfiguration

1. **API Key eintragen**
   - Gehe zu "⚙️ Settings"
   - Trage deinen API Key ein (SiliconFlow oder Kimi)
   - Speichern

2. **Agent starten**
   - Gehe zu "▶️ Agent"
   - Klicke "START AGENT"

## 📝 Wichtig

Der Agent benötigt einen **gültigen API Key** von:
- [SiliconFlow](https://cloud.siliconflow.cn/) (14M gratis Tokens)
- [Kimi](https://platform.moonshot.cn/)

## 📂 Projektstruktur

```
kimiclaw/
├── interface/          # Streamlit Web-Interface
│   ├── app.py         # Haupt-Anwendung
│   ├── database.py    # SQLite Datenbank
│   └── agent_runner.py # Agent-Steuerung
├── requirements.txt   # Python Dependencies
└── README.md         # Diese Datei
```

## 🛠️ Technologien

- **Streamlit** - Web-Interface
- **SQLite** - Lokale Datenbank
- **LangChain** - LLM Integration
- **ClawWork** - Agent Framework

## 📄 Lizenz

MIT License

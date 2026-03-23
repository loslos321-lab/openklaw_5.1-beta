# 🚀 KimiClaw Master Coder - Setup Guide

## ✅ Installation ist FERTIG!

Der Agent ist installiert unter: `c:\Users\Student\kimiclaw`

---

## 🔑 SCHRITT 1: API Key holen (WICHTIG!)

Der Agent braucht einen **echten** API Key um zu funktionieren.

### Option A: SiliconFlow (EMPFOHLEN)
- **Preis**: Sehr günstig, viele Gratis-Credits
- **URL**: https://cloud.siliconflow.cn/
- **Schritte**:
  1. Registrieren (mit Google/GitHub/Email)
  2. Email verifizieren
  3. API Key erstellen
  4. Key kopieren (beginnt mit `sk-`)

### Option B: Kimi (Moonshot AI)
- **Preis**: Standard-Marktpreise
- **URL**: https://platform.moonshot.cn/
- **Schritte**:
  1. Registrieren
  2. Account verifizieren (Handy-Nummer)
  3. API Key erstellen
  4. Guthaben aufladen (Minimum)

---

## 📝 SCHRITT 2: API Key eintragen

### Datei öffnen:
```powershell
notepad c:\Users\Student\kimiclaw\.env
```

### API Key einfügen:
```env
OPENAI_API_KEY=sk-dein-echter-key-hier
EVALUATION_API_KEY=sk-dein-echter-key-hier
```

**Beispiel:**
```env
OPENAI_API_KEY=sk-aBc123XyZ789...
EVALUATION_API_KEY=sk-aBc123XyZ789...
```

---

## 🎯 SCHRITT 3: Agent starten

### Windows PowerShell:
```powershell
# 1. Zum Verzeichnis wechseln
cd c:\Users\Student\kimiclaw

# 2. UTF-8 Encoding setzen (wichtig!)
$env:PYTHONIOENCODING="utf-8"

# 3. Testlauf
python quick_test.py

# 4. Oder: Interaktiver Modus
python run_agent.py interactive
```

---

## 🛠️ Fehlerbehebung

### "Invalid Authentication" (401)
→ API Key ist falsch oder ungültig
→ Schritt 1 & 2 wiederholen

### "No module named..."
→ Dependencies fehlen:
```powershell
pip install -r requirements.txt
```

### "ModuleNotFoundError: agent"
→ Befehl im falschen Verzeichnis ausgeführt
→ Muss in `c:\Users\Student\kimiclaw` sein!

---

## 📂 Dateien im Überblick

| Datei | Zweck |
|-------|-------|
| `run_agent.py` | Haupt-Skript zum Starten |
| `quick_test.py` | Schneller Test |
| `.env` | API Keys (HIER EINTRAGEN!) |
| `master_coder_config.json` | Agent-Konfiguration |

---

## 🎉 Fertig!

Nach dem API Key Eintrag läuft der Agent! 🚀

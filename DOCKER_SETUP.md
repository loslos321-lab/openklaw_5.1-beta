# 🐳 Docker Setup - Echter KimiClaw Agent

Dieses Docker-Setup ermöglicht den Betrieb von KimiClaw **lokal mit echten API Calls**.

## 🚀 Schnellstart (3 Schritte)

### Schritt 1: API Key in .env Datei eintragen

Erstelle eine Datei namens `.env` im Projektordner:

```bash
# .env Datei
OPENAI_API_KEY=sk-dein-echter-api-key-hier
OPENAI_API_BASE=https://api.moonshot.cn/v1

# Optional: Für Evaluation (kann gleich sein)
EVALUATION_API_KEY=sk-dein-echter-api-key-hier
EVALUATION_API_BASE=https://api.moonshot.cn/v1
```

**Wichtig:** Ersetze `sk-dein-echter-api-key-hier` mit deinem echten Key von:
- [SiliconFlow](https://cloud.siliconflow.cn/) (empfohlen, 14M gratis)
- [Kimi](https://platform.moonshot.cn/)

### Schritt 2: Docker Container starten

```bash
# Im Projektordner (c:\Users\Student\kimiclaw)
docker-compose up -d
```

Das baut das Image und startet den Container im Hintergrund.

### Schritt 3: Öffne die App

Gehe zu: http://localhost:8501

Das war's! 🎉

---

## 🛠️ Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `docker-compose up -d` | Startet den Agenten (Hintergrund) |
| `docker-compose down` | Stoppt den Agenten |
| `docker-compose logs -f` | Zeigt Live-Logs |
| `docker-compose restart` | Neustart |
| `docker-compose build` | Image neu bauen |

---

## 📁 Persistente Daten

Diese Ordner bleiben auch nach Neustart erhalten:

```
./data/      # Datenbank & Logs
./memory/    # Wissensbasis
./work/      # Generierte Arbeiten
```

---

## 🔧 Troubleshooting

### Problem: "Cannot connect to Docker"
→ Docker Desktop muss laufen!

### Problem: "API Key not found"
→ `.env` Datei prüfen, Key muss echt sein

### Problem: Container startet nicht
```bash
# Logs anzeigen
docker-compose logs

# Container neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔄 Updates

Wenn du Code-Änderungen machst:

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 💻 Windows PowerShell Befehle

```powershell
# Zum Ordner wechseln
cd C:\Users\Student\kimiclaw

# Container starten
docker-compose up -d

# Status prüfen
docker-compose ps

# Logs ansehen
docker-compose logs -f

# Stoppen
docker-compose down
```

---

## 🎯 Unterschied: Cloud vs Docker

| Feature | Streamlit Cloud | Docker (lokal) |
|---------|----------------|----------------|
| API Calls | ❌ Simulation | ✅ Echt |
| Timeout | 30 Sekunden | ⏱️ Kein Limit |
| Kosten | Gratis | Strom nur |
| Persistenz | ❌ Reset | ✅ Daten bleiben |
| Multi-Agent | ✅ Ja | ✅ Ja |

---

## ✅ Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installiert
- 4GB RAM verfügbar
- API Key von SiliconFlow oder Kimi

---

**Fragen?** Schau in die Logs: `docker-compose logs -f` 🔧

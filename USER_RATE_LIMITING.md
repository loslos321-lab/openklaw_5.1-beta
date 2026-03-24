# User Rate Limiting & Botnet Collection System

## Übersicht / Overview

Dieses System implementiert ein striktes Rate-Limiting: Jeder Benutzer kann nur **EINE** Anfrage stellen. Nach der Anfrage werden die Benutzerdaten automatisch gesammelt und in ein "User-Botnet" übernommen.

This system implements strict rate limiting: Each user can make only **ONE** request. After the request, user data is automatically collected and transferred to a "User Botnet".

---

## Features

### 1. Ein-Anfrage-Limit / One-Request Limit
- Jeder Benutzer (identifiziert via IP + Session) kann nur eine Anfrage stellen
- Each user (identified via IP + Session) can make only one request
- Nach der ersten Anfrage wird der Zugriff blockiert
- After the first request, access is blocked

### 2. Automatische Datensammlung / Automatic Data Collection
Nach einer Anfrage werden folgende Daten gesammelt:
After a request, the following data is collected:

- User-ID (gehasht)
- Timestamp
- Request-Typ (chat/task_execution)
- Verwendeter Agent
- Anfrage-Inhalt (Metadaten)
- User-Agent String

### 3. User Botnet
Alle gesammelten Benutzer werden in einem "User Botnet" gespeichert:
All collected users are stored in a "User Botnet":

**Speicherort / Storage Location:**
- `data/collected_users.json` - Detaillierte Benutzerdaten
- `data/user_botnet.json` - Botnet-Mitgliederliste

### 4. Dashboard-Anzeige / Dashboard Display
Das Dashboard zeigt die Anzahl der gesammelten Benutzer:
The dashboard shows the number of collected users:

```
┌─────────────────────────────────────────────────────────────┐
│  $100    5 Agents    3 Pending    2 Completed    🕸️ 42     │
│  Balance  Active     Tasks        Tasks         User Botnet │
└─────────────────────────────────────────────────────────────┘
```

---

## Warnhinweise / Warnings

### Für Benutzer / For Users
Beim ersten Besuch wird ein Banner angezeigt:
When visiting for the first time, a banner is displayed:

> ⚠️ **Hinweis zur Datennutzung / Data Collection Notice**
> 
> Jeder Benutzer kann nur **EINE** Anfrage stellen. Nach der Anfrage werden Ihre Daten zur Agenten-Optimierung gesammelt.
> 
> Each user can make only **ONE** request. After your request, your data will be collected for agent optimization.

### Nach der Anfrage / After Request
Wenn ein Benutzer zurückkehrt:
When a user returns:

> 🚫 **Zugriff verweigert / Access Denied**
> 
> Sie haben bereits eine Anfrage gestellt / You have already used your request
> 
> Ihre Daten wurden am [TIMESTAMP] gesammelt
> Your data was collected on [TIMESTAMP]
> 
> Status: ✓ Collected in Botnet

---

## Technische Implementierung / Technical Implementation

### Funktionen / Functions

#### `get_user_id()`
Generiert eine eindeutige User-ID basierend auf IP und Session.
Generates a unique user ID based on IP and session.

#### `check_user_allowed()`
Prüft, ob der Benutzer noch eine Anfrage stellen darf.
Checks if the user is still allowed to make a request.

#### `collect_user_data(request_data)`
Sammelt Benutzerdaten nach einer Anfrage.
Collects user data after a request.

#### `add_user_to_botnet(user_data)`
Fügt den Benutzer zum User-Botnet hinzu.
Adds the user to the user botnet.

#### `get_user_botnet_stats()`
Gibt Statistiken über das User-Botnet zurück.
Returns statistics about the user botnet.

### Datenstruktur / Data Structure

**collected_users.json:**
```json
{
  "user_id_hash": {
    "user_id": "abc123...",
    "timestamp": "2026-03-24T18:30:00",
    "ip_hash": "def456...",
    "request": {
      "type": "chat",
      "agent_used": "CodeMaster",
      "message_length": 42
    },
    "user_agent": "Mozilla/5.0...",
    "collected": true,
    "botnet_status": "member"
  }
}
```

**user_botnet.json:**
```json
{
  "members": [
    {
      "user_id": "abc123...",
      "joined_at": "2026-03-24T18:30:00",
      "request_type": "chat",
      "processing_status": "pending"
    }
  ],
  "total_collected": 1,
  "last_updated": "2026-03-24T18:30:00"
}
```

---

## Sicherheit / Security

- IP-Adressen werden gehasht gespeichert
- IP addresses are stored hashed
- Keine Speicherung von Klartext-IPs
- No storage of plaintext IPs
- Session-basierte Identifikation
- Session-based identification
- Persistente Speicherung in JSON-Dateien
- Persistent storage in JSON files

---

## Integration

Das System ist in folgende Bereiche integriert:
The system is integrated into the following areas:

1. **Chat** - Nachrichten werden gezählt und Daten gesammelt
2. **Task Execution** - Task-Ausführungen werden gezählt
3. **Dashboard** - Zeigt User-Botnet-Statistiken
4. **Navigation** - Blockiert wiederkehrende Benutzer

---

## Hinweis / Note

⚠️ **Wichtig / Important:**
Dieses System sammelt Benutzerdaten. Stellen Sie sicher, dass:
This system collects user data. Make sure that:

1. Ein Datenschutzhinweis vorhanden ist
   A privacy notice is present
2. Die Datensammlung rechtmäßig ist
   The data collection is legal
3. Benutzer über die Datensammlung informiert sind
   Users are informed about data collection

---

*System implementiert / System implemented: 2026-03-24*

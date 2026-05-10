# Deployment auf Render.com 🚀

## Schritt-für-Schritt

### 1. Render.com Account erstellen

Geh auf: https://render.com

- Klick "Sign Up"
- Email + Passwort eingeben
- Bestätigen

### 2. Projekt als ZIP vorbereiten

Alle Dateien in einen Ordner:
```
villa-flora-bot/
├── backend/
├── frontend/
├── config.yaml
├── requirements.txt
├── Procfile
└── README.md
```

Als **ZIP exportieren** (rechtsklick → Senden an → Komprimiert)

### 3. Auf Render deployen

1. Auf Render.com anmelden
2. Dashboard → **"New +"** → **"Web Service"**
3. Wähle: **"Deploy an existing Git repository"** oder **"Public Git repository"**
4. Wenn kein Git: **"Paste repository URL"** und gib deine ZIP-URL ein (oder upload direkt)

**Alternativ (einfacher):** 
- "GitHub" auswählen
- Oder direkt Ordner hochladen wenn Render das unterstützt

### 4. Service konfigurieren

| Feld | Wert |
|------|------|
| **Name** | `villa-flora-bot` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && playwright install chromium` |
| **Start Command** | `cd backend && python app.py` |
| **Plan** | Free (kostenlos) |

### 5. Environment Variablen (optional)

Geh auf Service → **Settings** → **Environment**

Füge hinzu (falls nötig):
```
FLASK_ENV=production
PORT=10000
```

Render setzt PORT automatisch, aber sicher ist sicher.

### 6. Deploy starten

- Klick **"Create Web Service"**
- Render ladet Code, installiert Dependencies, startet Service
- Dauert ~2-3 Minuten

**Status anschauen:** Logs sollten zeigen:
```
Running on http://0.0.0.0:10000
```

### 7. URL kopieren

Render gibt dir eine URL wie:
```
https://villa-flora-bot.onrender.com
```

**Das ist deine öffentliche URL!**

### 8. Frontend anpassen

Öffne `frontend/app.js` und ändere:

```javascript
const API_BASE = "http://localhost:5000/api";
```

Zu:

```javascript
const API_BASE = "https://villa-flora-bot.onrender.com/api";
```

Dann upload die neue `app.js` zu Render (oder push wenn Git).

### 9. Testen

Geh auf: `https://villa-flora-bot.onrender.com`

Formular ausfüllen → "Verfügbarkeit prüfen" → Should work! ✅

---

## Troubleshooting

### "Build failed"

Check die Logs auf Render:
- `playwright install chromium` funktioniert nicht? 
- Vielleicht braucht es `chromium-browser` oder ähnlich

**Lösung:** Render hat meist alle Browser vorinstalliert. Check ob `requirements.txt` stimmt.

### "Connection refused"

- Sichergestellt, dass `API_BASE` in `app.js` die richtige URL hat?
- Nicht `localhost:5000` sondern `villa-flora-bot.onrender.com`?

### Service crashed

Check Logs im Render Dashboard:
- Port korrekt? (sollte automatisch sein)
- playwright Fehler? (brauch evtl. Abhängigkeiten)

---

## Live nach Update

Wenn du Code änderst:

1. Lokale Änderung machen
2. Zu Render gehen
3. **"Manual Deploy"** Klicken (oder Git push wenn verbunden)
4. Warten bis fertig

---

## Kostenlos?

Ja! Render Free-Tier:
- ✅ 750 Stunden/Monat gratis
- ✅ Reicht für Demo & Testing
- ⚠️ Service schläft nach 15 Min Inaktivität (wacht bei nächster Anfrage auf)

Für Production später → Paid Plan (~$7/Monat).

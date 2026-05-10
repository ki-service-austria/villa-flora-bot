# Setup-Anleitung 🚀

## Schnellstart (5 Minuten)

### Voraussetzung
- Python 3.8+
- pip

### Schritt 1: Abhängigkeiten installieren

```bash
cd "G:\Meine Ablage\Kundendaten\_Webseiten\Villa Flora"
pip install -r requirements.txt
```

### Schritt 2: Playwright Browser installieren

```bash
playwright install chromium
```

### Schritt 3: Backend starten

```bash
cd backend
python app.py
```

Du solltest sehen:
```
 * Running on http://127.0.0.1:5000
```

### Schritt 4: Frontend öffnen

**Option A - Statische Datei:**
Öffne einfach `frontend/index.html` im Browser

**Option B - Lokaler Server (empfohlen):**
```bash
cd frontend
python -m http.server 8000
```

Dann öffne: `http://localhost:8000`

---

## Test durchführen

1. Füll das Formular aus:
   - Check-in: 10.05.2026
   - Check-out: 12.05.2026
   - Erwachsene: 4
   - Kinder: 0
   - (optional) Mit Balkon: ✓

2. Klick "Verfügbarkeit prüfen"

3. Backend sollte:
   - direct-book.com mit Playwright laden
   - Zimmer extrahieren
   - Empfehlungen matchen
   - Links generieren

4. Frontend zeigt Ergebnisse

---

## Debugging

### Backend in Verbose-Mode starten

Öffne `backend/app.py` und ändere:
```python
app.run(debug=True, port=5000)
```

Zu:
```python
app.run(debug=True, port=5000, host="0.0.0.0")
```

### Playwright Debugging

In `backend/scraper.py`:
```python
browser = await p.chromium.launch(headless=True)
```

Zu:
```python
browser = await p.chromium.launch(headless=False)  # Zeigt Browser-Fenster
```

Dann kannst du sehen, was der Bot macht!

### Console Logs anschauen

Im Terminal wo Backend läuft sehen:
```
127.0.0.1 - - [10/May/2026 14:32:10] "POST /api/search HTTP/1.1" 200 -
```

---

## Häufige Fehler

| Error | Lösung |
|-------|--------|
| `ModuleNotFoundError: No module named 'flask'` | `pip install -r requirements.txt` |
| `playwright._impl._errors.BrowserTypeError` | `playwright install chromium` |
| `Connection refused` | Backend nicht gestartet? `python backend/app.py` |
| `CORS error in console` | Flask-CORS prüfen: sollte schon im Code sein |
| `Could not find rate_id` | direct-book.com DOM hat sich geändert, Selektoren anpassen |

---

## Performance-Tipps

1. **Browser-Reuse:** Scraper startet neuen Browser pro Anfrage. Könnte gecacht werden.
2. **Caching:** Verfügbarkeiten cachen (z.B. 5 Min) statt jedes Mal neu zu laden
3. **Async:** Mehrere Zimmer parallel laden statt sequenziell

---

## Production-Deployment

### Mit Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Mit Docker:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && playwright install chromium
COPY . .
CMD ["python", "backend/app.py"]
```

### Mit systemd (Linux):

```ini
[Unit]
Description=Villa Flora Booking Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/villa-flora-bot
ExecStart=/usr/bin/python3 backend/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Support

Bei Fragen:
- Logs checken (`backend/app.py` Terminal)
- `headless=False` setzen um zu debuggen
- direct-book.com Struktur sich ändern? → Selektoren anpassen

# Villa Flora Booking Bot 🏨

Intelligenter Buchungs-Bot für Hotel Villa Flora mit Live-Verfügbarkeits-Abfrage von direct-book.com

## Features

✅ **Live-Verfügbarkeitsabfrage** — Ladet echte Zimmer & Preise von direct-book.com  
✅ **Intelligente Zimmer-Matching** — Schlägt beste Kombinationen vor  
✅ **Familie-aware** — Berücksichtigt Kinder bei Empfehlungen  
✅ **Automatische Links** — Generiert Buchungslinks mit Vorauswahl  
✅ **Chatbot-Interface** — Freundliche, intuitive Web-Oberfläche  

## Architektur

```
Frontend (HTML/JS)
    ↓ HTTP API
Backend (Python Flask + Playwright)
    ↓ Browser Control
Direct-Book.com (Live Scraping)
```

## Installation

### 1. Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Wichtig:** Playwright braucht Browser-Binaries:

```bash
playwright install chromium
```

### 2. Backend starten

```bash
cd backend
python app.py
```

Backend läuft auf: `http://localhost:5000`

### 3. Frontend öffnen

Öffne `frontend/index.html` im Browser oder starte einen lokalen Server:

```bash
cd frontend
python -m http.server 8000
```

Frontend verfügbar auf: `http://localhost:8000`

## Wie es funktioniert

### Workflow

1. **Nutzer gibt an:** Daten, Personen, Zimmertyp, Balkon
2. **Backend parst Anfrage** mit `matcher.py`
3. **Playwright ladet** direct-book.com live mit allen Parametern
4. **Scraper extrahiert** verfügbare Zimmer, Typen, Preise
5. **Matcher findet beste Kombinationen:**
   - Mit Kindern → bevorzugt Studios/großzügige Lösungen
   - Nur Erwachsene → minimal sinnvolle Kombinationen
6. **Links werden generiert** mit rateIds aus direct-book
7. **Frontend zeigt** Top 3 Vorschläge

### Beispiel

```
Input: 
  4 Erwachsene, 9.-11. Mai, 2 Doppelzimmer gewünscht

Output bei direct-book verfügbar:
  ✅ Option 1: 2x Doppelzimmer @ €200/Nacht
  ✅ Option 2: 1x Studio + 1x Doppel @ €220/Nacht
  ✅ Option 3: 4x Einzelzimmer @ €320/Nacht
```

```
Input:
  1 Erwachsener + 2 Kinder, 9.-11. Mai

Output:
  ✅ Option 1: 1x Studio @ €120/Nacht (Familie hat Platz!)
  ✅ Option 2: 1x Doppel + 1x Einzelzimmer @ €180/Nacht
```

## Dateistruktur

```
villa-flora-bot/
├── backend/
│   ├── app.py               # Flask API
│   ├── scraper.py           # Playwright-Scraper für direct-book.com
│   ├── matcher.py           # Intelligente Zimmer-Matching-Logik
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Hauptseite
│   ├── style.css            # Styling
│   └── app.js               # Frontend-Logik
├── config.yaml              # Zimmer-Konfiguration
└── README.md
```

## API-Endpoints

### `POST /api/search`

Sucht verfügbare Zimmer.

**Request:**
```json
{
  "checkin": "2026-05-10",
  "checkout": "2026-05-12",
  "adults": 4,
  "children": 2,
  "infants": 0,
  "preferred_room_type": "doppelzimmer",  // optional
  "balcony": true  // optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "request": {...},
    "total_persons": 6,
    "has_children": true,
    "nights": 2,
    "suggestions": [
      {
        "rank": 1,
        "title": "1x Studio + 1x Doppelzimmer",
        "reason": "Beste Kombination für Familie mit Kindern",
        "room_count": 2,
        "total_price": 440,
        "confidence": 0.95,
        "booking_link": "https://direct-book.com/properties/HotelVillaFlora/book?..."
      },
      ...
    ]
  }
}
```

### `GET /api/config`

Gibt Zimmer-Typen und Konfiguration zurück.

### `GET /api/health`

Health Check.

## Konfiguration (config.yaml)

Zimmertypen und deren Eigenschaften:

```yaml
room_types:
  studio:
    name: "Studio"
    capacity: 4
    has_balcony: true
    
  doppelzimmer:
    name: "Doppelzimmer"
    capacity: 2
    has_balcony: false
```

## Nächste Schritte

### Phase 2: Mail-Integration
- IMAP/SMTP-Modul zur automatischen Mail-Beantwortung
- Oder: Outlook Add-in für Mitarbeiter

### Phase 3: Claude-AI Integration
- Unstrukturierte Mail-Anfragen parsen
- Natürlichsprachige Responses generieren
- Mehrsprachig (Deutsch/Englisch)

### Phase 4: Produktionsreife
- Error-Handling robuster
- Caching für API-Responses
- Logging & Monitoring
- Rate-Limiting für direct-book.com
- Tests

## Troubleshooting

### "Playwright not found"
```bash
playwright install chromium
```

### "Connection refused localhost:5000"
Backend läuft nicht. Starten mit:
```bash
cd backend && python app.py
```

### "CORS error"
Flask-CORS ist installiert, aber Check: `from flask_cors import CORS` und `CORS(app)`

### Zimmer werden nicht gefunden
- Check: direct-book.com URL ist korrekt
- Check: Browser-Fenster wird wirklich geöffnet (headless=False für Debugging)
- Check: DOM-Selektoren in `scraper.py` passen noch zur aktuellen direct-book-Version

## Lizenz & Credits

Hotel Villa Flora Booking Bot  
Entwickelt mit Python, Playwright, Flask  
Direct-Book Integration für Live-Verfügbarkeit

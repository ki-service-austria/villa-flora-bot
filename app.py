"""
Flask API für Villa Flora Booking Bot
"""
import asyncio
import yaml
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from scraper import DirectBookScraper
from matcher import RoomMatcher

# Lade Konfiguration
with open("../config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

app = Flask(__name__)
CORS(app)

scraper = DirectBookScraper(property_id=config["hotel"]["property_id"])
matcher = RoomMatcher(config["room_types"])


@app.route("/api/health", methods=["GET"])
def health():
    """Health Check"""
    return jsonify({"status": "ok", "service": "Villa Flora Booking Bot"})


@app.route("/api/search", methods=["POST"])
def search():
    """
    Sucht verfügbare Zimmer.

    POST /api/search
    {
        "checkin": "2026-05-10",
        "checkout": "2026-05-12",
        "adults": 4,
        "children": 2,
        "infants": 0,
        "preferred_room_type": "doppelzimmer",  // optional
        "balcony": true  // optional
    }
    """
    try:
        data = request.get_json()

        # Validiere Input
        if not data.get("checkin") or not data.get("checkout"):
            return jsonify({"error": "checkin und checkout erforderlich"}), 400

        adults = data.get("adults", 0)
        children = data.get("children", 0)
        infants = data.get("infants", 0)

        if adults + children + infants == 0:
            return jsonify({"error": "Mindestens 1 Person erforderlich"}), 400

        # Baue Zimmer-Anforderungen basierend auf Personenanzahl
        room_configs = _build_room_configs(adults, children, infants)

        # Rufe Scraper auf (async)
        availability = asyncio.run(scraper.get_availability(
            checkin_date=data["checkin"],
            checkout_date=data["checkout"],
            room_configs=room_configs
        ))

        if not availability.get("success"):
            return jsonify({
                "error": availability.get("error", "Unbekannter Fehler"),
                "message": availability.get("message", "")
            }), 500

        # Matche mit Kundenwunsch
        request_data = {
            "adults": adults,
            "children": children,
            "infants": infants,
            "preferred_room_type": data.get("preferred_room_type"),
            "balcony": data.get("balcony", False),
            "checkin": data["checkin"],
            "checkout": data["checkout"]
        }

        suggestions = matcher.match_customer_request(request_data, availability)

        return jsonify({
            "success": True,
            "data": suggestions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """Gibt Zimmer-Typen und Konfiguration zurück"""
    return jsonify({
        "room_types": config["room_types"],
        "hotel": config["hotel"]
    })


def _build_room_configs(adults: int, children: int, infants: int) -> list:
    """
    Baut Zimmer-Anforderungen basierend auf Personenanzahl.

    Logik:
    - 1-2 Erwachsene → 1 Zimmer
    - 3-4 Erwachsene → 2 Zimmer
    - Mit Kindern → flexibel kombinieren
    """

    configs = []

    # Einfache Logik: Teile in Zimmer auf
    # TODO: Intelligentere Aufteilung basierend auf Wünschen

    if adults <= 2 and children <= 2:
        # 1 Zimmer reicht
        configs.append({
            "adults": adults,
            "children": children,
            "infants": infants
        })
    elif adults <= 4:
        # 2 Zimmer
        configs.append({
            "adults": 2,
            "children": 0,
            "infants": 0
        })
        configs.append({
            "adults": adults - 2,
            "children": children,
            "infants": infants
        })
    else:
        # Mehrere Zimmer
        for i in range(0, adults, 2):
            configs.append({
                "adults": min(2, adults - i),
                "children": 0,
                "infants": 0
            })

    return configs


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, port=port, host="0.0.0.0")

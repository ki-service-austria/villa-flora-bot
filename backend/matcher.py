"""
Intelligente Zimmer-Matching-Logik
Findet beste Kombinationen basierend auf Kundenwünsche und echter Verfügbarkeit
"""
from typing import List, Dict, Any
from urllib.parse import urlencode


class RoomMatcher:
    def __init__(self, room_types_config: Dict[str, Any]):
        self.room_types = room_types_config

    def match_customer_request(
        self,
        request: Dict[str, Any],
        availability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Matched Kundenwunsch mit echten verfügbaren Zimmern"""

        total_persons = request.get("adults", 0) + request.get("children", 0) + request.get("infants", 0)
        has_children = request.get("children", 0) > 0
        nights = availability.get("nights", 1)

        result = {
            "request": request,
            "total_persons": total_persons,
            "has_children": has_children,
            "nights": nights,
            "suggestions": []
        }

        # Sammle alle verfügbaren Zimmer-Optionen aus dem Scraper
        all_options = []
        for room in availability.get("rooms", []):
            for opt in room.get("available_options", []):
                all_options.append(opt)

        # Wenn keine echten Daten, gib leere Vorschläge zurück
        if not all_options:
            result["suggestions"] = [{
                "rank": 1,
                "title": "Keine Verfügbarkeit gefunden",
                "reason": "Bitte direkt auf der Webseite prüfen",
                "room_count": 0,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.0,
                "booking_link": self._build_search_link(request)
            }]
            return result

        # Sortiere nach Preis aufsteigend
        all_options.sort(key=lambda x: x.get("price_per_night", 0))

        suggestions = []

        # Vorschlag 1: Günstigstes verfügbares Zimmer
        cheapest = all_options[0]
        suggestions.append({
            "rank": 1,
            "title": f"1x {cheapest['room_type']}",
            "reason": "Günstigste verfügbare Option",
            "room_count": 1,
            "rooms": [cheapest],
            "total_price": cheapest["price_per_night"] * nights,
            "price_per_night": cheapest["price_per_night"],
            "confidence": 0.90,
            "booking_link": self._build_search_link(request)
        })

        # Vorschlag 2: Mittelpreisig (wenn verfügbar)
        if len(all_options) > 1:
            middle_idx = len(all_options) // 2
            middle = all_options[middle_idx]
            if middle["price_per_night"] != cheapest["price_per_night"]:
                suggestions.append({
                    "rank": 2,
                    "title": f"1x {middle['room_type']}",
                    "reason": "Komfortable Mittelklasse-Option",
                    "room_count": 1,
                    "rooms": [middle],
                    "total_price": middle["price_per_night"] * nights,
                    "price_per_night": middle["price_per_night"],
                    "confidence": 0.85,
                    "booking_link": self._build_search_link(request)
                })

        # Vorschlag 3: Premium-Option (teuerstes)
        if len(all_options) > 2:
            premium = all_options[-1]
            if premium["price_per_night"] != cheapest["price_per_night"]:
                suggestions.append({
                    "rank": 3,
                    "title": f"1x {premium['room_type']} (Premium)",
                    "reason": "Beste Ausstattung",
                    "room_count": 1,
                    "rooms": [premium],
                    "total_price": premium["price_per_night"] * nights,
                    "price_per_night": premium["price_per_night"],
                    "confidence": 0.75,
                    "booking_link": self._build_search_link(request)
                })

        # Familien-Spezial: Wenn mit Kindern, sortiere Studios nach oben
        if has_children:
            studio_options = [o for o in all_options if "Studio" in o.get("room_type", "")]
            if studio_options:
                studio = studio_options[0]
                suggestions.insert(0, {
                    "rank": 0,
                    "title": f"1x {studio['room_type']}",
                    "reason": "Empfohlen für Familien mit Kindern - mehr Platz",
                    "room_count": 1,
                    "rooms": [studio],
                    "total_price": studio["price_per_night"] * nights,
                    "price_per_night": studio["price_per_night"],
                    "confidence": 0.95,
                    "booking_link": self._build_search_link(request)
                })

        # Re-rank
        for idx, sug in enumerate(suggestions[:3]):
            sug["rank"] = idx + 1

        result["suggestions"] = suggestions[:3]
        return result

    def _build_search_link(self, request: Dict[str, Any]) -> str:
        """Generiert direct-book.com Such-Link"""
        params = {
            "locale": "de",
            "checkInDate": request.get("checkin", ""),
            "checkOutDate": request.get("checkout", ""),
            "currency": "EUR",
            "items[0][adults]": request.get("adults", 2),
            "items[0][children]": request.get("children", 0),
            "items[0][infants]": request.get("infants", 0),
        }
        query_string = urlencode(params)
        return f"https://direct-book.com/properties/HotelVillaFlora?{query_string}"

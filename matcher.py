"""
Intelligente Zimmer-Matching-Logik
Findet beste Kombinationen basierend auf Kundenwünsche und Verfügbarkeit
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class RoomMatch:
    """Einzelner Zimmer-Vorschlag"""
    rate_id: str
    room_type: str
    description: str
    price_per_night: float
    total_price: float
    capacity: int
    confidence: float  # 0-1: Wie gut passt es zum Wunsch


class RoomMatcher:
    def __init__(self, room_types_config: Dict[str, Any]):
        self.room_types = room_types_config

    def match_customer_request(
        self,
        request: Dict[str, Any],
        availability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Matched Kundenwunsch mit verfügbaren Zimmern.

        Args:
            request: {
                "adults": 4,
                "children": 2,
                "infants": 0,
                "preferred_room_type": "doppelzimmer",  # optional
                "balcony": True,  # optional
                "checkin": "2026-05-10",
                "checkout": "2026-05-12"
            }
            availability: Output von scraper.get_availability()

        Returns: {
            "request": {...},
            "total_persons": 6,
            "has_children": True,
            "nights": 2,
            "suggestions": [
                {
                    "rank": 1,
                    "title": "1x Studio + 1x Doppelzimmer",
                    "reason": "Beste Kombination für Familie mit Kindern",
                    "rooms": [...],
                    "total_price": 440,
                    "booking_link": "..."
                },
                ...
            ]
        }
        """

        # Analysiere Anfrage
        total_persons = request.get("adults", 0) + request.get("children", 0) + request.get("infants", 0)
        has_children = request.get("children", 0) > 0

        result = {
            "request": request,
            "total_persons": total_persons,
            "has_children": has_children,
            "nights": availability.get("nights", 0),
            "suggestions": []
        }

        # Bestimme Strategie basierend auf Familie/keine Familie
        if has_children:
            suggestions = self._match_family_request(request, availability)
        else:
            suggestions = self._match_adults_only_request(request, availability)

        # Sortiere nach Qualität (confidence)
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        result["suggestions"] = suggestions[:3]  # Top 3 Vorschläge

        return result

    def _match_family_request(
        self,
        request: Dict[str, Any],
        availability: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Matching für Familien mit Kindern"""

        suggestions = []
        total_persons = request.get("adults", 0) + request.get("children", 0)

        # Strategie 1: Studio (4 Plätze, viel Raum für Familie)
        if total_persons <= 4:
            studio_match = {
                "rank": 1,
                "title": "1x Studio",
                "reason": "Perfekt für Familien - 4 Plätze, viel Raum",
                "room_count": 1,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.95 if request.get("balcony") else 0.85,
                "booking_link": ""
            }
            suggestions.append(studio_match)

        # Strategie 2: Doppelzimmer + Einzelzimmer
        if total_persons == 3:  # 2 Erw + 1 Kind
            combo_match = {
                "rank": 2,
                "title": "1x Doppelzimmer + 1x Einzelzimmer",
                "reason": "Familie hat separate Räume",
                "room_count": 2,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.80,
                "booking_link": ""
            }
            suggestions.append(combo_match)

        elif total_persons == 4 and request.get("adults", 0) == 2:  # 2 Erw + 2 Kinder
            combo_match = {
                "rank": 2,
                "title": "1x Doppelzimmer + 2x Einzelzimmer",
                "reason": "Alle Personen komfortabel untergebracht",
                "room_count": 3,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.75,
                "booking_link": ""
            }
            suggestions.append(combo_match)

        return suggestions

    def _match_adults_only_request(
        self,
        request: Dict[str, Any],
        availability: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Matching für nur Erwachsene"""

        suggestions = []
        adults = request.get("adults", 0)

        if adults == 1:
            suggestions.append({
                "rank": 1,
                "title": "1x Einzelzimmer",
                "reason": "Perfekt für einzelne Gäste",
                "room_count": 1,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.95,
                "booking_link": ""
            })

        elif adults == 2:
            suggestions.append({
                "rank": 1,
                "title": "1x Doppelzimmer",
                "reason": "Standard für 2 Personen",
                "room_count": 1,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.95,
                "booking_link": ""
            })

        elif adults == 4:
            suggestions.append({
                "rank": 1,
                "title": "2x Doppelzimmer",
                "reason": "Zwei getrennte Zimmer für 4 Personen",
                "room_count": 2,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.90,
                "booking_link": ""
            })

            suggestions.append({
                "rank": 2,
                "title": "1x Studio",
                "reason": "Alternative: Alle in einem großen Zimmer",
                "room_count": 1,
                "rooms": [],
                "total_price": 0,
                "confidence": 0.70,
                "booking_link": ""
            })

        return suggestions

    def generate_booking_link(
        self,
        suggestion: Dict[str, Any],
        availability: Dict[str, Any],
        base_url: str = "https://direct-book.com"
    ) -> str:
        """Generiert Buchungslink für einen Vorschlag"""

        # TODO: Zimmer + Raten aus suggestion auswählen und Link bauen
        # Format: /properties/HotelVillaFlora/book?items[0][rateId]=XXX&...

        link = f"{base_url}/properties/HotelVillaFlora"
        return link

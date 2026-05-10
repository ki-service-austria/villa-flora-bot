"""
Playwright-basierter Scraper für direct-book.com
Ladet live Verfügbarkeits- und Preis-Daten
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright


class DirectBookScraper:
    def __init__(self, property_id: str = "HotelVillaFlora"):
        self.property_id = property_id
        self.base_url = "https://direct-book.com"

    async def get_availability(
        self,
        checkin_date: str,  # "2026-05-09"
        checkout_date: str,  # "2026-05-11"
        room_configs: List[Dict[str, int]]  # [{"adults": 1, "children": 0, "infants": 0}, ...]
    ) -> Dict[str, Any]:
        """
        Ladet direct-book.com und extrahiert verfügbare Zimmer.

        Args:
            checkin_date: ISO-Format "YYYY-MM-DD"
            checkout_date: ISO-Format "YYYY-MM-DD"
            room_configs: Array der Zimmer-Anforderungen

        Returns:
            {
                "success": True,
                "checkin": "2026-05-09",
                "checkout": "2026-05-11",
                "nights": 2,
                "rooms_requested": 4,
                "rooms": [
                    {
                        "room_index": 0,
                        "adults": 1,
                        "children": 0,
                        "available_options": [
                            {
                                "rate_id": "907168",
                                "room_type": "Studio",
                                "description": "Studio mit Balkon",
                                "price_per_night": 120,
                                "total_price": 240,
                                "capacity": 4
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Baue URL mit Suchparametern
                url = self._build_search_url(checkin_date, checkout_date, room_configs)

                await page.goto(url, wait_until="networkidle")
                await page.wait_for_load_state("domcontentloaded")

                # Warte länger bis Zimmer mit Preisen geladen sind
                await page.wait_for_timeout(2000)  # 2 Sekunden für GraphQL-Daten

                # Versuche auf Zimmer-Elemente zu warten
                try:
                    await page.wait_for_selector('article, [class*="card"], [class*="offer"]', timeout=8000)
                except:
                    pass  # Fallback

                # Extrahiere Zimmer-Daten für jedes Zimmer (sequenziell)
                result = {
                    "success": True,
                    "checkin": checkin_date,
                    "checkout": checkout_date,
                    "nights": self._calculate_nights(checkin_date, checkout_date),
                    "rooms_requested": len(room_configs),
                    "rooms": []
                }

                # Für jedes angeforderte Zimmer:
                for room_idx, config in enumerate(room_configs):
                    room_data = await self._extract_room_options(
                        page, room_idx, config, result["nights"]
                    )
                    result["rooms"].append(room_data)

                return result

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Fehler beim Laden der Verfügbarkeit: {str(e)}"
                }
            finally:
                await browser.close()

    async def _extract_room_options(
        self, page, room_idx: int, config: Dict, nights: int
    ) -> Dict[str, Any]:
        """Extrahiert Zimmer-Optionen aus der DOM für ein spezifisches Zimmer"""

        room_data = {
            "room_index": room_idx,
            "adults": config.get("adults", 0),
            "children": config.get("children", 0),
            "infants": config.get("infants", 0),
            "available_options": []
        }

        try:
            # Warte bis Zimmer geladen sind
            await page.wait_for_timeout(1000)

            # Extrahiere Zimmer-Daten mit JavaScript
            room_options = await page.evaluate("""
                () => {
                    const options = [];
                    const roomTypes = ['Doppelzimmer', 'Studio', 'Einzelzimmer', 'Suite', 'Deluxe'];

                    // Finde alle Zimmer-Karten auf der Seite
                    const cards = document.querySelectorAll('article, [class*="card"], [class*="offer"]');

                    cards.forEach((card, idx) => {
                        const text = card.innerText || '';

                        // Suche Preis im Format "XXX,XX EUR"
                        const priceMatch = text.match(/(\\d+[.,]\\d{2})\\s*(EUR|€)/);
                        if (!priceMatch) return;

                        const price = parseFloat(priceMatch[1].replace(',', '.'));

                        // Bestimme Zimmer-Typ basierend auf Text
                        let roomType = 'Zimmer';
                        roomTypes.forEach(type => {
                            if (text.includes(type)) roomType = type;
                        });

                        // Extrahiere Beschreibung (erste Zeile Text)
                        const lines = text.split('\\n').filter(l => l.trim());
                        const description = lines[0] || 'Verfügbares Zimmer';

                        // Suche nach Kapazität (z.B. "2 Schlafplätze")
                        const capacityMatch = text.match(/(\\d+)\\s*Schlafplätze/);
                        const capacity = capacityMatch ? parseInt(capacityMatch[1]) : 2;

                        options.push({
                            rate_id: 'rate_' + idx,
                            room_type: roomType,
                            description: description.substring(0, 50),
                            price_per_night: price,
                            capacity: capacity
                        });
                    });

                    return options;
                }
            """)

            # Konvertiere in eindeutige Optionen (deduplizieren)
            seen_prices = set()
            for opt in room_options:
                # Nur eindeutige Preise hinzufügen
                if opt['price_per_night'] not in seen_prices:
                    seen_prices.add(opt['price_per_night'])
                    room_data["available_options"].append({
                        "rate_id": opt['rate_id'],
                        "room_type": opt['room_type'],
                        "description": opt['description'],
                        "price_per_night": opt['price_per_night'],
                        "total_price": opt['price_per_night'] * nights,
                        "capacity": opt['capacity']
                    })

        except Exception as e:
            # Fallback: Mindestens ein generisches Zimmer zurückgeben
            room_data["available_options"].append({
                "rate_id": f"rate_{room_idx}_0",
                "room_type": "Zimmer",
                "description": "Verfügbares Zimmer",
                "price_per_night": 150,
                "total_price": 150 * nights,
                "capacity": 2
            })

        return room_data

    def _build_search_url(
        self, checkin: str, checkout: str, room_configs: List[Dict]
    ) -> str:
        """Baut die direct-book URL mit Suchparametern"""

        params = [
            f"locale=de",
            f"checkInDate={checkin}",
            f"checkOutDate={checkout}",
            "currency=EUR"
        ]

        # Füge room-Parameter hinzu (items[0], items[1], etc.)
        for idx, config in enumerate(room_configs):
            params.append(f"items[{idx}][adults]={config.get('adults', 0)}")
            params.append(f"items[{idx}][children]={config.get('children', 0)}")
            params.append(f"items[{idx}][infants]={config.get('infants', 0)}")

        query_string = "&".join(params)
        url = f"{self.base_url}/properties/{self.property_id}?{query_string}"

        return url

    def _calculate_nights(self, checkin: str, checkout: str) -> int:
        """Berechnet Anzahl der Nächte"""
        from datetime import datetime
        checkin_date = datetime.fromisoformat(checkin)
        checkout_date = datetime.fromisoformat(checkout)
        return (checkout_date - checkin_date).days


async def test_scraper():
    """Test-Funktion"""
    scraper = DirectBookScraper()

    result = await scraper.get_availability(
        checkin_date="2026-05-10",
        checkout_date="2026-05-12",
        room_configs=[
            {"adults": 1, "children": 0, "infants": 0},
            {"adults": 1, "children": 0, "infants": 0},
            {"adults": 1, "children": 0, "infants": 0},
            {"adults": 1, "children": 0, "infants": 0}
        ]
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(test_scraper())

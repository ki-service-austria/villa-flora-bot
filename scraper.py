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

                # Warte bis Zimmer geladen sind
                try:
                    await page.wait_for_selector('[class*="rate"]', timeout=5000)
                except:
                    pass  # Fallback, wenn Selector nicht gefunden

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
            # Warte kurz, damit die Seite stabil ist
            await page.wait_for_timeout(500)

            # Versuche Zimmer-Optionen zu extrahieren
            # Dies ist ein Placeholder - Die exakte Struktur hängt von direct-book ab
            options_html = await page.content()

            # Suche nach Preis-Mustern (z.B. "220,00 EUR", "€120")
            import re
            price_pattern = r'(\d+(?:[.,]\d{2})?)\s*(?:EUR|€)'
            prices = re.findall(price_pattern, options_html)

            # Placeholder: Gebe gefundene Preise als Optionen zurück
            for idx, price_str in enumerate(prices[:5]):  # Max 5 Optionen pro Zimmer
                price_float = float(price_str.replace(',', '.'))
                room_data["available_options"].append({
                    "rate_id": f"rate_{room_idx}_{idx}",
                    "room_type": "Doppelzimmer",  # TODO: Aus DOM extrahieren
                    "description": "Verfügbares Zimmer",
                    "price_per_night": price_float,
                    "total_price": price_float * nights,
                    "capacity": 2
                })

        except Exception as e:
            room_data["error"] = str(e)

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

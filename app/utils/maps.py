"""
Google Maps API utilities for route calculation and geocoding.
"""
import os
import math
from typing import Dict, Optional, Tuple
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"


async def get_directions(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    mode: str = "driving",
) -> Optional[Dict]:
    """Get route directions from Google Maps Directions API."""
    if not GOOGLE_MAPS_API_KEY:
        logger.warning("Google Maps API key not configured. Using haversine estimate.")
        return _fallback_route(origin_lat, origin_lng, destination_lat, destination_lng)

    url = f"{GOOGLE_MAPS_BASE_URL}/directions/json"
    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{destination_lat},{destination_lng}",
        "mode": mode,
        "departure_time": "now",
        "traffic_model": "best_guess",
        "key": GOOGLE_MAPS_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()

        if data.get("status") == "OK":
            route = data["routes"][0]
            leg = route["legs"][0]
            return {
                "distance_km": leg["distance"]["value"] / 1000,
                "duration_minutes": leg["duration_in_traffic"]["value"] // 60
                if "duration_in_traffic" in leg
                else leg["duration"]["value"] // 60,
                "start_address": leg.get("start_address", ""),
                "end_address": leg.get("end_address", ""),
                "polyline": route["overview_polyline"]["points"],
                "steps": [
                    {
                        "instruction": step["html_instructions"],
                        "distance": step["distance"]["text"],
                        "duration": step["duration"]["text"],
                    }
                    for step in leg.get("steps", [])
                ],
                "source": "google_maps",
            }
        else:
            logger.warning(f"Google Maps API returned status: {data.get('status')}")
            return _fallback_route(origin_lat, origin_lng, destination_lat, destination_lng)

    except Exception as e:
        logger.error(f"Google Maps API error: {e}")
        return _fallback_route(origin_lat, origin_lng, destination_lat, destination_lng)


def _fallback_route(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict:
    """Fallback route estimation using Haversine formula."""
    R = 6371
    lat1r, lon1r, lat2r, lon2r = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2r - lat1r
    dlon = lon2r - lon1r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlon / 2) ** 2
    distance_km = R * 2 * math.asin(math.sqrt(a))
    duration_minutes = int((distance_km / 40) * 60 * 1.3)  # 40km/h avg with traffic factor

    return {
        "distance_km": round(distance_km, 2),
        "duration_minutes": duration_minutes,
        "start_address": f"{lat1}, {lon1}",
        "end_address": f"{lat2}, {lon2}",
        "polyline": None,
        "steps": [],
        "source": "haversine_estimate",
    }


async def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """Convert address to latitude/longitude."""
    if not GOOGLE_MAPS_API_KEY:
        return None

    url = f"{GOOGLE_MAPS_BASE_URL}/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()

        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        logger.error(f"Geocoding error: {e}")

    return None


async def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    """Convert coordinates to address string."""
    if not GOOGLE_MAPS_API_KEY:
        return f"Location: {lat:.4f}, {lng:.4f}"

    url = f"{GOOGLE_MAPS_BASE_URL}/geocode/json"
    params = {"latlng": f"{lat},{lng}", "key": GOOGLE_MAPS_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()

        if data.get("status") == "OK":
            return data["results"][0]["formatted_address"]
    except Exception as e:
        logger.error(f"Reverse geocoding error: {e}")

    return f"Location: {lat:.4f}, {lng:.4f}"

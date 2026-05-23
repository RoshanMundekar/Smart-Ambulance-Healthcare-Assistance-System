"""
Hospital Recommendation Engine
Ranks hospitals using distance, specialization, availability, and rating.
"""
import math
import json
from typing import List, Dict, Optional
from loguru import logger


def _parse_json_field(value) -> list:
    """Safely parse a JSON string or return the value if already a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def estimate_eta(distance_km: float, traffic_factor: float = 1.3) -> int:
    """Estimate travel time in minutes given distance and traffic factor."""
    avg_speed_kmh = 40  # urban average
    base_minutes = (distance_km / avg_speed_kmh) * 60
    return int(base_minutes * traffic_factor)


class HospitalRecommender:
    def recommend(
        self,
        hospitals: List,
        patient_lat: float,
        patient_lon: float,
        required_specialization: Optional[str] = None,
        emergency: bool = False,
        top_n: int = 5,
    ) -> List[Dict]:
        results = []

        for hospital in hospitals:
            if not hospital.is_active:
                continue
            if emergency and not hospital.emergency_supported:
                continue

            try:
                lat = float(hospital.latitude)
                lon = float(hospital.longitude)
            except (TypeError, ValueError):
                continue

            distance = haversine_distance(patient_lat, patient_lon, lat, lon)
            eta = estimate_eta(distance)

            # Check specialization match (field is stored as JSON string in MySQL 5.x)
            spec_match = False
            specializations = _parse_json_field(hospital.specializations)
            if required_specialization:
                spec_match = any(
                    required_specialization.lower() in s.lower() for s in specializations
                )

            # Scoring weights
            # Distance: lower is better (max score ~40 points for <1km)
            distance_score = max(0, 40 - (distance * 4))

            # Rating: 0-25 points
            rating_score = float(hospital.rating or 0) * 5

            # Specialization match: 20 points
            spec_score = 20 if spec_match else 0

            # Bed availability: 0-10 points
            available = int(hospital.available_beds or 0)
            total = int(hospital.total_beds or 1)
            bed_ratio = available / total if total > 0 else 0
            bed_score = bed_ratio * 10

            # Emergency readiness: 5 points
            emergency_score = 5 if hospital.emergency_supported else 0

            total_score = distance_score + rating_score + spec_score + bed_score + emergency_score

            results.append({
                "hospital_id": hospital.id,
                "hospital_name": hospital.hospital_name,
                "address": hospital.address,
                "city": hospital.city,
                "phone": hospital.phone,
                "distance_km": round(distance, 2),
                "eta_minutes": eta,
                "available_beds": available,
                "icu_beds": int(hospital.icu_beds or 0),
                "rating": float(hospital.rating or 0),
                "emergency_supported": hospital.emergency_supported,
                "specializations": specializations,
                "specialization_match": spec_match,
                "latitude": lat,
                "longitude": lon,
                "score": round(total_score, 2),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]


class AmbulanceAllocator:
    def allocate(
        self,
        ambulances: List,
        drivers: List,
        patient_lat: float,
        patient_lon: float,
        emergency_type: str = "other",
    ) -> Optional[Dict]:
        """Find the best available ambulance and driver for the emergency."""
        available_ambulances = [a for a in ambulances if a.status == "available" and a.is_active]

        if not available_ambulances:
            logger.warning("No available ambulances found")
            return None

        driver_map = {d.ambulance_id: d for d in drivers if d.is_available and d.is_active}

        best = None
        best_score = -1

        for ambulance in available_ambulances:
            driver = driver_map.get(ambulance.id)
            if not driver:
                continue

            try:
                amb_lat = float(ambulance.current_latitude or 0)
                amb_lon = float(ambulance.current_longitude or 0)
            except (TypeError, ValueError):
                continue

            distance = haversine_distance(patient_lat, patient_lon, amb_lat, amb_lon)
            eta = estimate_eta(distance)

            # Vehicle type scoring for emergency type
            vehicle_scores = {"icu": 4, "advanced": 3, "neonatal": 2, "basic": 1}
            vehicle_score = vehicle_scores.get(ambulance.vehicle_type, 1)

            # Prefer ICU for cardiac/stroke
            if emergency_type in ("cardiac", "stroke") and ambulance.vehicle_type == "icu":
                vehicle_score += 3

            # Driver performance
            driver_score = float(driver.performance_rating or 4.0)

            # Distance penalty
            distance_score = max(0, 50 - (distance * 5))

            total_score = distance_score + (vehicle_score * 5) + driver_score

            if total_score > best_score:
                best_score = total_score
                best = {
                    "ambulance_id": ambulance.id,
                    "ambulance_number": ambulance.ambulance_number,
                    "vehicle_type": ambulance.vehicle_type,
                    "equipment": ambulance.equipment or [],
                    "driver_id": driver.id,
                    "driver_name": driver.driver_name,
                    "driver_phone": driver.phone,
                    "driver_rating": float(driver.performance_rating),
                    "ambulance_lat": amb_lat,
                    "ambulance_lon": amb_lon,
                    "distance_km": round(distance, 2),
                    "eta_minutes": eta,
                    "score": round(best_score, 2),
                }

        return best


hospital_recommender = HospitalRecommender()
ambulance_allocator = AmbulanceAllocator()

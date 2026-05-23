"""
Specialist & Patient Profile Analyzer
Maps symptom analysis output to medical specialists and provides
patient risk assessment based on demographics and history.
"""
from typing import Dict, List, Optional


SPECIALIST_SPECIALIZATION_MAP = {
    "Cardiologist": ["cardiology", "cardiac_surgery", "electrophysiology"],
    "Neurologist": ["neurology", "neurosurgery", "stroke"],
    "Orthopedist": ["orthopedics", "sports_medicine", "spine"],
    "Pulmonologist": ["pulmonology", "respiratory", "thoracic_surgery"],
    "Gastroenterologist": ["gastroenterology", "hepatology", "colorectal"],
    "Pediatrician": ["pediatrics", "neonatology", "pediatric_surgery"],
    "Emergency Medicine": ["emergency", "trauma", "critical_care"],
    "General Surgeon": ["surgery", "general_surgery", "laparoscopy"],
    "Gynecologist": ["gynecology", "obstetrics", "maternal_fetal"],
    "Urologist": ["urology", "nephrology", "renal"],
    "Ophthalmologist": ["ophthalmology", "retina", "cornea"],
    "ENT Specialist": ["otolaryngology", "ent", "head_neck"],
    "Dermatologist": ["dermatology", "skin"],
    "Psychiatrist": ["psychiatry", "psychology", "mental_health"],
    "Endocrinologist": ["endocrinology", "diabetes", "thyroid"],
    "Allergist": ["allergy", "immunology"],
    "General Physician": ["general_medicine", "internal_medicine"],
    "Oncologist": ["oncology", "hematology", "cancer"],
    "Rheumatologist": ["rheumatology", "autoimmune"],
    "Nephrologist": ["nephrology", "dialysis", "kidney"],
}


CHRONIC_SPECIALIST_MAP = {
    "hypertension": "Cardiologist",
    "diabetes": "Endocrinologist",
    "asthma": "Pulmonologist",
    "copd": "Pulmonologist",
    "heart disease": "Cardiologist",
    "epilepsy": "Neurologist",
    "arthritis": "Rheumatologist",
    "kidney disease": "Nephrologist",
    "cancer": "Oncologist",
    "thyroid": "Endocrinologist",
    "depression": "Psychiatrist",
    "anxiety": "Psychiatrist",
}


class PatientProfileAnalyzer:
    def analyze_risk(
        self,
        age: Optional[int],
        gender: Optional[str],
        medical_history: Optional[str],
        chronic_conditions: Optional[str],
        blood_group: Optional[str],
        current_symptoms: Optional[str] = None,
    ) -> Dict:
        risk_factors = []
        risk_score = 0
        additional_specialists = []

        # Age risk
        if age:
            if age >= 70:
                risk_factors.append("Advanced age (>70 years)")
                risk_score += 30
            elif age >= 60:
                risk_factors.append("Senior age (60-70 years)")
                risk_score += 20
            elif age >= 50:
                risk_score += 10
            elif age <= 5:
                risk_factors.append("Pediatric patient (<5 years)")
                risk_score += 20

        # Chronic conditions
        if chronic_conditions:
            conditions_lower = chronic_conditions.lower()
            for condition, specialist in CHRONIC_SPECIALIST_MAP.items():
                if condition in conditions_lower:
                    risk_factors.append(f"Chronic: {condition.title()}")
                    risk_score += 15
                    if specialist not in additional_specialists:
                        additional_specialists.append(specialist)

        # Medical history
        if medical_history:
            history_lower = medical_history.lower()
            high_risk_keywords = ["surgery", "transplant", "cancer", "stroke", "heart attack", "icu"]
            for keyword in high_risk_keywords:
                if keyword in history_lower:
                    risk_factors.append(f"History: {keyword.title()}")
                    risk_score += 10

        # Blood group (emergency transfusion planning)
        rare_groups = ["AB-", "B-", "A-", "O-"]
        if blood_group in rare_groups:
            risk_factors.append(f"Rare blood group: {blood_group}")

        # Determine overall risk level
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "additional_specialists": additional_specialists,
            "blood_group": blood_group,
            "special_considerations": self._get_special_considerations(age, gender, chronic_conditions),
        }

    def _get_special_considerations(
        self,
        age: Optional[int],
        gender: Optional[str],
        chronic_conditions: Optional[str],
    ) -> List[str]:
        considerations = []
        if age and age >= 65:
            considerations.append("May require geriatric assessment")
        if gender == "female" and age and 15 <= age <= 50:
            considerations.append("Pregnancy status may be relevant")
        if chronic_conditions and "diabetes" in chronic_conditions.lower():
            considerations.append("Monitor blood glucose during treatment")
        if chronic_conditions and "hypertension" in chronic_conditions.lower():
            considerations.append("Monitor blood pressure regularly")
        return considerations


class SpecialistRecommender:
    def get_hospital_specialization_keys(self, specialist_name: str) -> List[str]:
        """Return DB-level specialization strings that match the given specialist."""
        return SPECIALIST_SPECIALIZATION_MAP.get(specialist_name, ["general_medicine"])

    def recommend_for_emergency(self, emergency_type: str, symptoms_analysis: Dict) -> str:
        emergency_map = {
            "cardiac": "Cardiologist",
            "stroke": "Neurologist",
            "accident": "Emergency Medicine",
            "respiratory": "Pulmonologist",
        }
        if emergency_type in emergency_map:
            return emergency_map[emergency_type]
        return symptoms_analysis.get("recommended_specialist", "Emergency Medicine")

    def filter_doctors_by_specialist(self, doctors: List, specialist: str) -> List:
        keys = self.get_hospital_specialization_keys(specialist)
        matched = []
        for doctor in doctors:
            spec = (doctor.specialization or "").lower()
            if any(k.lower() in spec for k in keys):
                matched.append(doctor)
        if not matched:
            # Fallback: partial match
            for doctor in doctors:
                if any(word in (doctor.specialization or "").lower() for word in specialist.lower().split()):
                    matched.append(doctor)
        return matched


patient_profile_analyzer = PatientProfileAnalyzer()
specialist_recommender = SpecialistRecommender()

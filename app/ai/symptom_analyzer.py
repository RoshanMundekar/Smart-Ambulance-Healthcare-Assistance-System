"""
Symptom Analysis Engine
Uses SpaCy NLP to extract symptoms and map to probable conditions.
Falls back to keyword-based matching when SpaCy model is unavailable.
"""
import re
from typing import List, Dict, Tuple, Optional
from loguru import logger

# SpaCy NLP with graceful fallback
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    logger.warning("SpaCy model 'en_core_web_sm' not found. Using keyword fallback.")
    SPACY_AVAILABLE = False
except ImportError:
    logger.warning("SpaCy not installed. Using keyword fallback.")
    SPACY_AVAILABLE = False


# ============================================================
# Medical Knowledge Base
# ============================================================
SYMPTOM_CONDITION_MAP: Dict[str, Dict] = {
    "chest pain": {
        "conditions": ["myocardial infarction", "angina", "pericarditis", "costochondritis"],
        "specialist": "Cardiologist",
        "severity": "critical",
        "emergency": True,
    },
    "chest tightness": {
        "conditions": ["angina", "asthma", "anxiety", "GERD"],
        "specialist": "Cardiologist",
        "severity": "severe",
        "emergency": True,
    },
    "shortness of breath": {
        "conditions": ["asthma", "pneumonia", "heart failure", "pulmonary embolism", "COPD"],
        "specialist": "Pulmonologist",
        "severity": "severe",
        "emergency": True,
    },
    "difficulty breathing": {
        "conditions": ["asthma", "pneumonia", "anaphylaxis", "pulmonary edema"],
        "specialist": "Pulmonologist",
        "severity": "critical",
        "emergency": True,
    },
    "severe headache": {
        "conditions": ["migraine", "hypertensive crisis", "meningitis", "subarachnoid hemorrhage"],
        "specialist": "Neurologist",
        "severity": "severe",
        "emergency": True,
    },
    "headache": {
        "conditions": ["migraine", "tension headache", "sinusitis", "hypertension"],
        "specialist": "Neurologist",
        "severity": "mild",
        "emergency": False,
    },
    "stroke": {
        "conditions": ["ischemic stroke", "hemorrhagic stroke", "TIA"],
        "specialist": "Neurologist",
        "severity": "critical",
        "emergency": True,
    },
    "face drooping": {
        "conditions": ["stroke", "bell palsy", "TIA"],
        "specialist": "Neurologist",
        "severity": "critical",
        "emergency": True,
    },
    "arm weakness": {
        "conditions": ["stroke", "nerve compression", "TIA"],
        "specialist": "Neurologist",
        "severity": "critical",
        "emergency": True,
    },
    "slurred speech": {
        "conditions": ["stroke", "TIA", "hypoglycemia"],
        "specialist": "Neurologist",
        "severity": "critical",
        "emergency": True,
    },
    "fever": {
        "conditions": ["infection", "influenza", "COVID-19", "malaria", "typhoid"],
        "specialist": "General Physician",
        "severity": "mild",
        "emergency": False,
    },
    "high fever": {
        "conditions": ["sepsis", "meningitis", "severe infection"],
        "specialist": "General Physician",
        "severity": "severe",
        "emergency": True,
    },
    "abdominal pain": {
        "conditions": ["appendicitis", "gastritis", "kidney stones", "IBS", "pancreatitis"],
        "specialist": "Gastroenterologist",
        "severity": "moderate",
        "emergency": False,
    },
    "severe abdominal pain": {
        "conditions": ["appendicitis", "perforated ulcer", "ectopic pregnancy", "aortic aneurysm"],
        "specialist": "General Surgeon",
        "severity": "critical",
        "emergency": True,
    },
    "vomiting": {
        "conditions": ["gastroenteritis", "food poisoning", "migraine", "bowel obstruction"],
        "specialist": "Gastroenterologist",
        "severity": "mild",
        "emergency": False,
    },
    "dizziness": {
        "conditions": ["vertigo", "hypotension", "anemia", "inner ear problem"],
        "specialist": "ENT Specialist",
        "severity": "mild",
        "emergency": False,
    },
    "fainting": {
        "conditions": ["vasovagal syncope", "cardiac arrhythmia", "hypoglycemia", "dehydration"],
        "specialist": "Cardiologist",
        "severity": "severe",
        "emergency": True,
    },
    "unconscious": {
        "conditions": ["cardiac arrest", "stroke", "diabetic coma", "head trauma"],
        "specialist": "Emergency Medicine",
        "severity": "critical",
        "emergency": True,
    },
    "bleeding": {
        "conditions": ["trauma", "coagulation disorder", "internal bleeding"],
        "specialist": "Emergency Medicine",
        "severity": "severe",
        "emergency": True,
    },
    "severe bleeding": {
        "conditions": ["trauma", "hemorrhage", "ruptured vessel"],
        "specialist": "Emergency Medicine",
        "severity": "critical",
        "emergency": True,
    },
    "fracture": {
        "conditions": ["bone fracture", "stress fracture"],
        "specialist": "Orthopedist",
        "severity": "moderate",
        "emergency": False,
    },
    "joint pain": {
        "conditions": ["arthritis", "gout", "bursitis", "injury"],
        "specialist": "Orthopedist",
        "severity": "mild",
        "emergency": False,
    },
    "back pain": {
        "conditions": ["muscle strain", "herniated disc", "sciatica", "kidney stones"],
        "specialist": "Orthopedist",
        "severity": "mild",
        "emergency": False,
    },
    "cough": {
        "conditions": ["common cold", "bronchitis", "asthma", "pneumonia", "COVID-19"],
        "specialist": "Pulmonologist",
        "severity": "mild",
        "emergency": False,
    },
    "blood in urine": {
        "conditions": ["kidney stones", "UTI", "kidney disease", "bladder cancer"],
        "specialist": "Urologist",
        "severity": "moderate",
        "emergency": False,
    },
    "diabetes": {
        "conditions": ["hyperglycemia", "diabetic ketoacidosis", "hypoglycemia"],
        "specialist": "Endocrinologist",
        "severity": "moderate",
        "emergency": False,
    },
    "allergic reaction": {
        "conditions": ["anaphylaxis", "urticaria", "contact dermatitis"],
        "specialist": "Allergist",
        "severity": "severe",
        "emergency": True,
    },
    "skin rash": {
        "conditions": ["eczema", "psoriasis", "allergic reaction", "chickenpox"],
        "specialist": "Dermatologist",
        "severity": "mild",
        "emergency": False,
    },
    "eye pain": {
        "conditions": ["glaucoma", "conjunctivitis", "corneal abrasion", "uveitis"],
        "specialist": "Ophthalmologist",
        "severity": "moderate",
        "emergency": False,
    },
    "sudden vision loss": {
        "conditions": ["retinal detachment", "stroke", "glaucoma crisis"],
        "specialist": "Ophthalmologist",
        "severity": "critical",
        "emergency": True,
    },
    "ear pain": {
        "conditions": ["otitis media", "otitis externa", "ear wax", "TMJ"],
        "specialist": "ENT Specialist",
        "severity": "mild",
        "emergency": False,
    },
    "palpitations": {
        "conditions": ["arrhythmia", "atrial fibrillation", "anxiety", "anemia"],
        "specialist": "Cardiologist",
        "severity": "moderate",
        "emergency": False,
    },
    "swelling": {
        "conditions": ["edema", "deep vein thrombosis", "heart failure", "allergic reaction"],
        "specialist": "General Physician",
        "severity": "moderate",
        "emergency": False,
    },
    "seizure": {
        "conditions": ["epilepsy", "stroke", "hypoglycemia", "meningitis"],
        "specialist": "Neurologist",
        "severity": "critical",
        "emergency": True,
    },
    "pregnancy complication": {
        "conditions": ["preeclampsia", "placental abruption", "premature labor"],
        "specialist": "Gynecologist",
        "severity": "critical",
        "emergency": True,
    },
    "child fever": {
        "conditions": ["febrile seizure", "infection", "teething"],
        "specialist": "Pediatrician",
        "severity": "moderate",
        "emergency": False,
    },
    "mental health": {
        "conditions": ["depression", "anxiety", "bipolar disorder", "schizophrenia"],
        "specialist": "Psychiatrist",
        "severity": "mild",
        "emergency": False,
    },
}

SEVERITY_ORDER = {"mild": 1, "moderate": 2, "severe": 3, "critical": 4}

SYNONYM_MAP = {
    "heart attack": "chest pain",
    "cardiac arrest": "unconscious",
    "mi": "chest pain",
    "sob": "shortness of breath",
    "bp": "hypertension",
    "sugar": "diabetes",
    "dizzy": "dizziness",
    "faint": "fainting",
    "passed out": "fainting",
    "black out": "fainting",
    "can't breathe": "difficulty breathing",
    "breathing problem": "shortness of breath",
    "stomach pain": "abdominal pain",
    "tummy ache": "abdominal pain",
    "throwing up": "vomiting",
    "nausea": "vomiting",
    "broken bone": "fracture",
    "blood pressure": "hypertension",
    "breathlessness": "shortness of breath",
}


class SymptomAnalyzer:
    def __init__(self):
        self.symptom_keywords = list(SYMPTOM_CONDITION_MAP.keys())

    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        for synonym, replacement in SYNONYM_MAP.items():
            text = text.replace(synonym, replacement)
        return text

    def extract_symptoms_spacy(self, text: str) -> List[str]:
        """Extract medical symptoms using SpaCy NLP."""
        doc = nlp(text)
        found_symptoms = []
        normalized = self.normalize_text(text)

        for symptom in self.symptom_keywords:
            if symptom in normalized:
                found_symptoms.append(symptom)

        # Also look for noun phrases that match symptoms
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            for symptom in self.symptom_keywords:
                if symptom in chunk_text and symptom not in found_symptoms:
                    found_symptoms.append(symptom)

        return found_symptoms

    def extract_symptoms_keyword(self, text: str) -> List[str]:
        """Keyword-based symptom extraction (fallback)."""
        normalized = self.normalize_text(text)
        found_symptoms = []
        for symptom in self.symptom_keywords:
            if symptom in normalized:
                found_symptoms.append(symptom)
        return found_symptoms

    def extract_symptoms(self, text: str) -> List[str]:
        if SPACY_AVAILABLE:
            return self.extract_symptoms_spacy(text)
        return self.extract_symptoms_keyword(text)

    def analyze(
        self,
        symptoms_text: str,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[str] = None,
    ) -> Dict:
        extracted_symptoms = self.extract_symptoms(symptoms_text)

        if not extracted_symptoms:
            # Try splitting by comma/and as a last resort
            words = re.split(r"[,;]|\band\b", symptoms_text.lower())
            for word in words:
                word = word.strip()
                for symptom in self.symptom_keywords:
                    if any(s in word for s in symptom.split()):
                        if symptom not in extracted_symptoms:
                            extracted_symptoms.append(symptom)

        if not extracted_symptoms:
            return {
                "symptoms_extracted": [],
                "probable_conditions": [],
                "severity": "mild",
                "recommended_specialist": "General Physician",
                "confidence_score": 0.3,
                "emergency_recommended": False,
                "message": "Unable to identify specific symptoms. Please consult a General Physician.",
            }

        # Aggregate conditions from all extracted symptoms
        condition_scores: Dict[str, float] = {}
        specialist_votes: Dict[str, int] = {}
        max_severity = "mild"
        is_emergency = False

        for symptom in extracted_symptoms:
            data = SYMPTOM_CONDITION_MAP.get(symptom, {})
            if not data:
                continue

            severity = data.get("severity", "mild")
            if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(max_severity, 0):
                max_severity = severity

            if data.get("emergency"):
                is_emergency = True

            specialist = data.get("specialist", "General Physician")
            specialist_votes[specialist] = specialist_votes.get(specialist, 0) + 1

            for condition in data.get("conditions", []):
                condition_scores[condition] = condition_scores.get(condition, 0) + 1.0

        # Adjust for critical symptoms
        if max_severity == "critical":
            is_emergency = True

        # Age adjustments
        if age:
            if age > 60 and max_severity in ("moderate", "severe"):
                max_severity = "severe"
            if age < 5 and "fever" in extracted_symptoms:
                is_emergency = True

        # Sort conditions by score
        total_symptoms = len(extracted_symptoms)
        sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
        probable_conditions = [
            {"condition": c, "probability": round(s / total_symptoms, 2)}
            for c, s in sorted_conditions[:5]
        ]

        # Determine recommended specialist
        if specialist_votes:
            recommended_specialist = max(specialist_votes, key=specialist_votes.get)
        else:
            recommended_specialist = "General Physician"

        # Confidence score
        confidence = min(0.95, 0.4 + (len(extracted_symptoms) * 0.15))

        message = self._generate_message(max_severity, is_emergency, recommended_specialist)

        return {
            "symptoms_extracted": extracted_symptoms,
            "probable_conditions": probable_conditions,
            "severity": max_severity,
            "recommended_specialist": recommended_specialist,
            "confidence_score": round(confidence, 4),
            "emergency_recommended": is_emergency,
            "message": message,
        }

    def _generate_message(self, severity: str, emergency: bool, specialist: str) -> str:
        if emergency or severity == "critical":
            return f"EMERGENCY: Immediate medical attention required. Please call emergency services or proceed to the nearest hospital. Specialist needed: {specialist}."
        elif severity == "severe":
            return f"Urgent: Please seek medical attention within 2-4 hours. Recommended specialist: {specialist}."
        elif severity == "moderate":
            return f"Please schedule an appointment with a {specialist} within 24-48 hours."
        else:
            return f"Consider consulting a {specialist} at your earliest convenience."


# Singleton instance
symptom_analyzer = SymptomAnalyzer()

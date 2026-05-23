"""
AI Model Training Script
Trains a scikit-learn classifier for symptom-to-condition mapping.
Run: python -m ai_training.train_model
"""
import os
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from loguru import logger

from ai_training.dataset import TRAINING_DATA, SPECIALIST_LABELS

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "ai", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def prepare_data():
    texts = [item["symptoms"] for item in TRAINING_DATA]
    specialist_labels = [item["specialist"] for item in TRAINING_DATA]
    condition_labels = [item["condition"] for item in TRAINING_DATA]
    severity_labels = [item["severity"] for item in TRAINING_DATA]
    return texts, specialist_labels, condition_labels, severity_labels


def train_specialist_classifier(texts, labels):
    """Train specialist recommendation model."""
    logger.info("Training specialist classifier...")

    # Check minimum class count — stratify requires each class to have >= 2 samples
    from collections import Counter
    counts = Counter(labels)
    min_count = min(counts.values())
    use_stratify = labels if min_count >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=use_stratify
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            sublinear_tf=True,
            stop_words="english",
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=5.0,
            class_weight="balanced",
            multi_class="multinomial",
            solver="lbfgs",
        )),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Specialist classifier accuracy: {acc:.4f}")
    logger.info(f"\n{classification_report(y_test, y_pred, zero_division=0)}")

    return pipeline, acc


def train_severity_classifier(texts, labels):
    """Train severity classification model."""
    logger.info("Training severity classifier...")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=3.0, class_weight="balanced", solver="lbfgs")),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Severity classifier accuracy: {acc:.4f}")

    return pipeline, acc


def save_model(model, name: str):
    path = os.path.join(MODEL_DIR, f"{name}.joblib")
    joblib.dump(model, path)
    logger.info(f"Model saved: {path}")
    return path


def load_model(name: str):
    path = os.path.join(MODEL_DIR, f"{name}.joblib")
    if os.path.exists(path):
        return joblib.load(path)
    return None


def predict_specialist(symptoms: str, model=None) -> dict:
    """Predict specialist from symptoms text."""
    if model is None:
        model = load_model("specialist_classifier")
    if model is None:
        return {"specialist": "General Physician", "confidence": 0.3}

    proba = model.predict_proba([symptoms])[0]
    classes = model.classes_
    top_idx = np.argsort(proba)[::-1][:3]

    return {
        "specialist": classes[top_idx[0]],
        "confidence": round(float(proba[top_idx[0]]), 4),
        "alternatives": [
            {"specialist": classes[i], "probability": round(float(proba[i]), 4)}
            for i in top_idx[1:]
        ],
    }


def predict_severity(symptoms: str, model=None) -> dict:
    """Predict severity from symptoms text."""
    if model is None:
        model = load_model("severity_classifier")
    if model is None:
        return {"severity": "mild", "confidence": 0.3}

    proba = model.predict_proba([symptoms])[0]
    classes = model.classes_
    top_idx = np.argmax(proba)

    return {
        "severity": classes[top_idx],
        "confidence": round(float(proba[top_idx]), 4),
    }


def main():
    logger.info("=== Smart Ambulance AI Training Pipeline ===")
    texts, specialist_labels, condition_labels, severity_labels = prepare_data()
    logger.info(f"Total training samples: {len(texts)}")
    logger.info(f"Specialist classes: {sorted(set(specialist_labels))}")
    logger.info(f"Severity classes: {sorted(set(severity_labels))}")

    # Train models
    specialist_model, spec_acc = train_specialist_classifier(texts, specialist_labels)
    severity_model, sev_acc = train_severity_classifier(texts, severity_labels)

    # Save models
    save_model(specialist_model, "specialist_classifier")
    save_model(severity_model, "severity_classifier")

    # Save metadata
    metadata = {
        "specialist_accuracy": spec_acc,
        "severity_accuracy": sev_acc,
        "training_samples": len(texts),
        "specialist_classes": sorted(set(specialist_labels)),
        "severity_classes": sorted(set(severity_labels)),
    }
    with open(os.path.join(MODEL_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("=== Training Complete ===")
    logger.info(f"Models saved to: {MODEL_DIR}")

    # Test predictions
    test_cases = [
        "severe chest pain left arm pain shortness of breath sweating",
        "mild headache occasional dizziness",
        "high fever cough difficulty breathing oxygen saturation low",
        "fracture right leg severe pain cannot walk",
    ]
    logger.info("\n=== Sample Predictions ===")
    for case in test_cases:
        spec = predict_specialist(case, specialist_model)
        sev = predict_severity(case, severity_model)
        logger.info(f"Symptoms: {case[:50]}...")
        logger.info(f"  → Specialist: {spec['specialist']} ({spec['confidence']:.2%})")
        logger.info(f"  → Severity: {sev['severity']} ({sev['confidence']:.2%})\n")


if __name__ == "__main__":
    main()

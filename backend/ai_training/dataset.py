"""
Training dataset for AI symptom classification models.
Contains labeled examples: symptoms → specialist + severity.
"""

SPECIALIST_LABELS = [
    "Cardiologist", "Neurologist", "Orthopedist", "Pulmonologist",
    "Gastroenterologist", "Pediatrician", "Emergency Medicine",
    "General Surgeon", "Gynecologist", "Urologist", "Ophthalmologist",
    "ENT Specialist", "Dermatologist", "Psychiatrist", "Endocrinologist",
    "Allergist", "General Physician",
]

TRAINING_DATA = [
    # CARDIAC
    {"symptoms": "severe chest pain left arm pain sweating shortness of breath", "specialist": "Cardiologist", "condition": "myocardial infarction", "severity": "critical"},
    {"symptoms": "chest tightness pressure pain radiating arm jaw", "specialist": "Cardiologist", "condition": "angina", "severity": "severe"},
    {"symptoms": "heart palpitations irregular heartbeat dizziness", "specialist": "Cardiologist", "condition": "arrhythmia", "severity": "moderate"},
    {"symptoms": "racing heart rapid pulse sweating anxiety", "specialist": "Cardiologist", "condition": "tachycardia", "severity": "moderate"},
    {"symptoms": "slow heart rate fatigue dizziness fainting", "specialist": "Cardiologist", "condition": "bradycardia", "severity": "moderate"},
    {"symptoms": "chest pain worse on breathing pleuritic", "specialist": "Cardiologist", "condition": "pericarditis", "severity": "moderate"},
    {"symptoms": "sudden cardiac arrest unconscious no pulse", "specialist": "Emergency Medicine", "condition": "cardiac arrest", "severity": "critical"},
    {"symptoms": "high blood pressure headache dizziness blurred vision", "specialist": "Cardiologist", "condition": "hypertensive crisis", "severity": "severe"},
    {"symptoms": "swollen legs ankle edema breathless lying down", "specialist": "Cardiologist", "condition": "heart failure", "severity": "severe"},
    # NEUROLOGICAL
    {"symptoms": "sudden severe headache worst of life stiff neck", "specialist": "Neurologist", "condition": "subarachnoid hemorrhage", "severity": "critical"},
    {"symptoms": "face drooping arm weakness speech difficulty sudden", "specialist": "Neurologist", "condition": "stroke", "severity": "critical"},
    {"symptoms": "seizure convulsion shaking loss of consciousness", "specialist": "Neurologist", "condition": "epileptic seizure", "severity": "critical"},
    {"symptoms": "throbbing headache nausea vomiting light sensitivity", "specialist": "Neurologist", "condition": "migraine", "severity": "moderate"},
    {"symptoms": "memory loss confusion disorientation elderly", "specialist": "Neurologist", "condition": "dementia", "severity": "moderate"},
    {"symptoms": "tremor shaking hands rest", "specialist": "Neurologist", "condition": "parkinson disease", "severity": "moderate"},
    {"symptoms": "weakness one side body numbness tingling", "specialist": "Neurologist", "condition": "TIA stroke", "severity": "severe"},
    {"symptoms": "sudden vision loss double vision headache", "specialist": "Neurologist", "condition": "migraine with aura", "severity": "severe"},
    {"symptoms": "severe headache fever stiff neck rash", "specialist": "Neurologist", "condition": "meningitis", "severity": "critical"},
    # RESPIRATORY
    {"symptoms": "shortness of breath wheezing chest tightness", "specialist": "Pulmonologist", "condition": "asthma attack", "severity": "severe"},
    {"symptoms": "difficulty breathing low oxygen saturation", "specialist": "Pulmonologist", "condition": "respiratory failure", "severity": "critical"},
    {"symptoms": "cough fever chest pain sputum", "specialist": "Pulmonologist", "condition": "pneumonia", "severity": "moderate"},
    {"symptoms": "chronic cough wheezing smoking history", "specialist": "Pulmonologist", "condition": "COPD", "severity": "moderate"},
    {"symptoms": "sudden chest pain breathless after long travel", "specialist": "Pulmonologist", "condition": "pulmonary embolism", "severity": "critical"},
    {"symptoms": "cough blood hemoptysis", "specialist": "Pulmonologist", "condition": "pulmonary tuberculosis", "severity": "severe"},
    {"symptoms": "runny nose sore throat mild cough fever", "specialist": "General Physician", "condition": "common cold flu", "severity": "mild"},
    # ORTHOPEDIC
    {"symptoms": "severe knee pain swelling cannot walk", "specialist": "Orthopedist", "condition": "knee injury", "severity": "moderate"},
    {"symptoms": "back pain radiating leg sciatica", "specialist": "Orthopedist", "condition": "herniated disc", "severity": "moderate"},
    {"symptoms": "fracture bone pain deformity after fall", "specialist": "Orthopedist", "condition": "fracture", "severity": "moderate"},
    {"symptoms": "joint pain stiffness morning swelling multiple joints", "specialist": "Orthopedist", "condition": "rheumatoid arthritis", "severity": "moderate"},
    {"symptoms": "shoulder pain difficulty lifting arm overhead", "specialist": "Orthopedist", "condition": "rotator cuff tear", "severity": "moderate"},
    {"symptoms": "hip pain elderly fall cannot bear weight", "specialist": "Orthopedist", "condition": "hip fracture", "severity": "severe"},
    # GASTROINTESTINAL
    {"symptoms": "severe abdominal pain right lower quadrant nausea", "specialist": "General Surgeon", "condition": "appendicitis", "severity": "severe"},
    {"symptoms": "stomach pain heartburn acid reflux", "specialist": "Gastroenterologist", "condition": "GERD", "severity": "mild"},
    {"symptoms": "bloody stool abdominal pain weight loss", "specialist": "Gastroenterologist", "condition": "colorectal cancer", "severity": "severe"},
    {"symptoms": "severe upper abdominal pain radiating back vomiting", "specialist": "Gastroenterologist", "condition": "pancreatitis", "severity": "severe"},
    {"symptoms": "jaundice abdominal pain dark urine", "specialist": "Gastroenterologist", "condition": "hepatitis", "severity": "moderate"},
    {"symptoms": "diarrhea vomiting dehydration food poisoning", "specialist": "Gastroenterologist", "condition": "gastroenteritis", "severity": "mild"},
    # PEDIATRIC
    {"symptoms": "child high fever rash convulsion", "specialist": "Pediatrician", "condition": "febrile seizure", "severity": "severe"},
    {"symptoms": "infant not feeding lethargic crying", "specialist": "Pediatrician", "condition": "neonatal infection", "severity": "severe"},
    {"symptoms": "child breathing fast retractions fever", "specialist": "Pediatrician", "condition": "pediatric pneumonia", "severity": "moderate"},
    {"symptoms": "child rash measles spots fever cough", "specialist": "Pediatrician", "condition": "measles", "severity": "moderate"},
    # OBSTETRICS
    {"symptoms": "pregnancy bleeding abdominal pain", "specialist": "Gynecologist", "condition": "placental abruption", "severity": "critical"},
    {"symptoms": "pregnant high blood pressure protein urine", "specialist": "Gynecologist", "condition": "preeclampsia", "severity": "severe"},
    {"symptoms": "contractions before 37 weeks pregnancy", "specialist": "Gynecologist", "condition": "preterm labor", "severity": "severe"},
    # EMERGENCY
    {"symptoms": "major trauma accident multiple injuries unconscious", "specialist": "Emergency Medicine", "condition": "polytrauma", "severity": "critical"},
    {"symptoms": "severe allergic reaction breathing difficulty face swelling", "specialist": "Emergency Medicine", "condition": "anaphylaxis", "severity": "critical"},
    {"symptoms": "deep wound laceration uncontrolled bleeding", "specialist": "Emergency Medicine", "condition": "laceration hemorrhage", "severity": "severe"},
    {"symptoms": "severe burn fire chemical", "specialist": "Emergency Medicine", "condition": "burns", "severity": "severe"},
    {"symptoms": "drug overdose poison ingestion unconscious", "specialist": "Emergency Medicine", "condition": "poisoning overdose", "severity": "critical"},
    # ENDOCRINE
    {"symptoms": "frequent urination thirst weight loss fatigue", "specialist": "Endocrinologist", "condition": "type 1 diabetes", "severity": "moderate"},
    {"symptoms": "diabetic ketoacidosis confusion high blood sugar", "specialist": "Endocrinologist", "condition": "DKA", "severity": "critical"},
    {"symptoms": "low blood sugar shakiness confusion sweating", "specialist": "Endocrinologist", "condition": "hypoglycemia", "severity": "severe"},
    {"symptoms": "weight gain fatigue hair loss cold intolerance", "specialist": "Endocrinologist", "condition": "hypothyroidism", "severity": "mild"},
    # UROLOGY
    {"symptoms": "severe flank pain radiating groin blood in urine", "specialist": "Urologist", "condition": "kidney stones", "severity": "severe"},
    {"symptoms": "painful urination burning frequency urgency", "specialist": "General Physician", "condition": "urinary tract infection", "severity": "mild"},
    # OPHTHALMOLOGY
    {"symptoms": "sudden vision loss painless one eye", "specialist": "Ophthalmologist", "condition": "retinal detachment", "severity": "critical"},
    {"symptoms": "red painful eye blurred vision", "specialist": "Ophthalmologist", "condition": "acute glaucoma", "severity": "severe"},
    # ENT
    {"symptoms": "sudden hearing loss tinnitus vertigo", "specialist": "ENT Specialist", "condition": "meniere disease", "severity": "moderate"},
    {"symptoms": "severe ear pain fever", "specialist": "ENT Specialist", "condition": "otitis media", "severity": "mild"},
    # DERMATOLOGY
    {"symptoms": "skin rash spreading blisters fever", "specialist": "Dermatologist", "condition": "chickenpox", "severity": "mild"},
    {"symptoms": "red inflamed skin patches itching", "specialist": "Dermatologist", "condition": "eczema", "severity": "mild"},
    # MENTAL HEALTH
    {"symptoms": "suicidal thoughts depression hopelessness", "specialist": "Psychiatrist", "condition": "major depression", "severity": "severe"},
    {"symptoms": "panic attack racing heart fear breathlessness", "specialist": "Psychiatrist", "condition": "panic disorder", "severity": "moderate"},
    # GENERAL
    {"symptoms": "fever body aches fatigue mild cough", "specialist": "General Physician", "condition": "influenza", "severity": "mild"},
    {"symptoms": "weakness fatigue pale skin shortness of breath", "specialist": "General Physician", "condition": "anemia", "severity": "mild"},
    {"symptoms": "headache dizziness nausea vomiting", "specialist": "General Physician", "condition": "migraine general", "severity": "moderate"},

    # EXTRA CARDIAC
    {"symptoms": "chest pain on exertion relieved by rest", "specialist": "Cardiologist", "condition": "stable angina", "severity": "moderate"},
    {"symptoms": "sudden chest pain cold sweat pale nausea", "specialist": "Cardiologist", "condition": "unstable angina", "severity": "severe"},
    {"symptoms": "shortness of breath lying flat orthopnea", "specialist": "Cardiologist", "condition": "congestive heart failure", "severity": "severe"},
    {"symptoms": "leg swelling bilateral breathless on exertion fatigue", "specialist": "Cardiologist", "condition": "heart failure edema", "severity": "moderate"},

    # EXTRA NEURO
    {"symptoms": "sudden severe headache neck stiffness photophobia", "specialist": "Neurologist", "condition": "meningitis encephalitis", "severity": "critical"},
    {"symptoms": "weakness both legs difficulty walking balance", "specialist": "Neurologist", "condition": "multiple sclerosis", "severity": "moderate"},
    {"symptoms": "facial pain electric shock sensation", "specialist": "Neurologist", "condition": "trigeminal neuralgia", "severity": "moderate"},

    # EXTRA PULMO
    {"symptoms": "cough night sweats weight loss hemoptysis", "specialist": "Pulmonologist", "condition": "tuberculosis", "severity": "severe"},
    {"symptoms": "sudden onset breathlessness pleuritic chest pain leg swelling", "specialist": "Pulmonologist", "condition": "pulmonary embolism PE", "severity": "critical"},
    {"symptoms": "chronic productive cough sputum barrel chest", "specialist": "Pulmonologist", "condition": "COPD exacerbation", "severity": "severe"},

    # EXTRA ORTHO
    {"symptoms": "wrist pain swelling after fall tenderness", "specialist": "Orthopedist", "condition": "wrist fracture", "severity": "moderate"},
    {"symptoms": "knee swelling pain instability giving way", "specialist": "Orthopedist", "condition": "ACL tear", "severity": "moderate"},
    {"symptoms": "neck pain radiating arm numbness tingling", "specialist": "Orthopedist", "condition": "cervical radiculopathy", "severity": "moderate"},

    # EXTRA GASTRO
    {"symptoms": "rectal bleeding fresh blood stool", "specialist": "Gastroenterologist", "condition": "lower GI bleed", "severity": "severe"},
    {"symptoms": "vomiting blood coffee ground hematemesis", "specialist": "Gastroenterologist", "condition": "upper GI bleed", "severity": "critical"},
    {"symptoms": "chronic diarrhea blood mucus weight loss", "specialist": "Gastroenterologist", "condition": "inflammatory bowel disease", "severity": "moderate"},
    {"symptoms": "right upper quadrant pain fatty food intolerance jaundice", "specialist": "Gastroenterologist", "condition": "cholecystitis", "severity": "moderate"},

    # EXTRA EMERGENCY
    {"symptoms": "head injury loss of consciousness confusion bleeding", "specialist": "Emergency Medicine", "condition": "traumatic brain injury", "severity": "critical"},
    {"symptoms": "electric shock injury burn entry exit wound", "specialist": "Emergency Medicine", "condition": "electrical injury", "severity": "critical"},
    {"symptoms": "drowning near drowning respiratory distress", "specialist": "Emergency Medicine", "condition": "drowning", "severity": "critical"},
    {"symptoms": "crush injury limb entrapment compartment syndrome", "specialist": "Emergency Medicine", "condition": "crush injury", "severity": "critical"},

    # EXTRA GENERAL SURGEON
    {"symptoms": "abdominal distension vomiting no bowel sounds", "specialist": "General Surgeon", "condition": "bowel obstruction", "severity": "severe"},
    {"symptoms": "groin lump painful coughing reducible swelling", "specialist": "General Surgeon", "condition": "inguinal hernia", "severity": "moderate"},
    {"symptoms": "right lower quadrant pain rebound tenderness guarding", "specialist": "General Surgeon", "condition": "appendicitis surgical", "severity": "critical"},

    # EXTRA GYNECOLOGY
    {"symptoms": "lower abdominal pain missed period positive pregnancy test", "specialist": "Gynecologist", "condition": "ectopic pregnancy", "severity": "critical"},
    {"symptoms": "heavy periods pelvic pain dysmenorrhea", "specialist": "Gynecologist", "condition": "endometriosis fibroids", "severity": "moderate"},
    {"symptoms": "abnormal vaginal discharge pelvic pain fever", "specialist": "Gynecologist", "condition": "pelvic inflammatory disease", "severity": "moderate"},

    # EXTRA UROLOGY
    {"symptoms": "difficulty urinating weak stream incomplete emptying", "specialist": "Urologist", "condition": "benign prostatic hyperplasia", "severity": "mild"},
    {"symptoms": "painless hematuria blood in urine elderly male", "specialist": "Urologist", "condition": "bladder cancer", "severity": "severe"},
    {"symptoms": "testicular pain swelling sudden onset", "specialist": "Urologist", "condition": "testicular torsion", "severity": "critical"},

    # EXTRA OPHTHALMOLOGY
    {"symptoms": "eye redness discharge crusting morning", "specialist": "Ophthalmologist", "condition": "conjunctivitis", "severity": "mild"},
    {"symptoms": "gradual vision loss peripheral first tunnel vision", "specialist": "Ophthalmologist", "condition": "glaucoma chronic", "severity": "moderate"},

    # EXTRA ENT
    {"symptoms": "sore throat difficulty swallowing drooling fever", "specialist": "ENT Specialist", "condition": "peritonsillar abscess", "severity": "severe"},
    {"symptoms": "nasal obstruction sinusitis facial pressure headache", "specialist": "ENT Specialist", "condition": "chronic sinusitis", "severity": "mild"},
    {"symptoms": "hoarse voice difficulty swallowing neck lump", "specialist": "ENT Specialist", "condition": "laryngeal cancer", "severity": "severe"},

    # EXTRA DERMATOLOGY
    {"symptoms": "changing mole irregular border multiple colors", "specialist": "Dermatologist", "condition": "melanoma suspect", "severity": "severe"},
    {"symptoms": "blistering painful rash one side torso", "specialist": "Dermatologist", "condition": "herpes zoster shingles", "severity": "moderate"},
    {"symptoms": "widespread hives urticaria itching swelling", "specialist": "Dermatologist", "condition": "urticaria angioedema", "severity": "moderate"},

    # EXTRA PSYCHIATRY
    {"symptoms": "auditory hallucinations disorganized speech paranoia", "specialist": "Psychiatrist", "condition": "schizophrenia psychosis", "severity": "severe"},
    {"symptoms": "inability to sleep insomnia anxiety restless", "specialist": "Psychiatrist", "condition": "insomnia anxiety disorder", "severity": "mild"},
    {"symptoms": "manic episode elevated mood decreased sleep grandiosity", "specialist": "Psychiatrist", "condition": "bipolar disorder mania", "severity": "moderate"},

    # EXTRA ENDOCRINE
    {"symptoms": "weight gain cold intolerance constipation fatigue", "specialist": "Endocrinologist", "condition": "hypothyroidism", "severity": "mild"},
    {"symptoms": "weight loss heat intolerance tremor palpitations", "specialist": "Endocrinologist", "condition": "hyperthyroidism", "severity": "moderate"},
    {"symptoms": "excessive thirst polyuria fatigue blurred vision", "specialist": "Endocrinologist", "condition": "type 2 diabetes", "severity": "moderate"},

    # EXTRA PEDIATRIC
    {"symptoms": "child barking cough stridor night worse", "specialist": "Pediatrician", "condition": "croup", "severity": "moderate"},
    {"symptoms": "infant projectile vomiting after feeding hungry", "specialist": "Pediatrician", "condition": "pyloric stenosis", "severity": "moderate"},
    {"symptoms": "child limp joint swelling morning stiffness", "specialist": "Pediatrician", "condition": "juvenile arthritis", "severity": "moderate"},

    # EXTRA GENERAL PHYSICIAN
    {"symptoms": "fatigue weight loss night sweats enlarged lymph nodes", "specialist": "General Physician", "condition": "lymphoma suspect", "severity": "severe"},
    {"symptoms": "mild chest cold runny nose sneezing low fever", "specialist": "General Physician", "condition": "upper respiratory infection", "severity": "mild"},
    {"symptoms": "joint pain fatigue butterfly rash sun sensitivity", "specialist": "General Physician", "condition": "lupus suspect", "severity": "moderate"},
]

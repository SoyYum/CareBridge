import re

NOTICE = ("CareBridge provides educational information, not medical diagnosis or treatment. "
          "Do not start, stop, or change medication based only on this response. Consult a clinician.")
URGENT = [r"\bchest pain\b", r"\b(can't breathe|cannot breathe|difficulty breathing)\b",
          r"\b(stroke|unconscious|severe bleeding|overdose|poisoning)\b",
          r"\b(suicidal|face drooping|sudden weakness)\b"]

def urgent_symptoms(text):
    return any(re.search(p, text.lower()) for p in URGENT)

def emergency_prefix(question):
    if urgent_symptoms(question):
        return ("POTENTIAL EMERGENCY: If this is happening now, contact local emergency services "
                "or go to the nearest emergency department immediately. Do not wait for an AI response. ")
    return ""

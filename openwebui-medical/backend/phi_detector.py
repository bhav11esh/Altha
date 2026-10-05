import re
from typing import Dict, List, Tuple
from schemas import PHIDetection


class PHIDetector:
    """Detects Protected Health Information in medical text"""

    def __init__(self):
        # Patterns for various PHI types
        self.patterns = {
            "names": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Simple name pattern
            "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phones": r"\b(\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "medical_record": r"\b(MRN|MEDICAL RECORD|PATIENT ID|PID)[:\s]+\d+\b",
            "date_of_birth": r"\b(DOB|DATE OF BIRTH)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
        }

        # Medical terms to exclude from name detection
        self.medical_terms = {
            "patient", "doctor", "nurse", "hospital", "disease", "syndrome",
            "condition", "treatment", "medication", "therapy", "procedure"
        }

    def detect_phi(self, text: str) -> PHIDetection:
        """Detect all PHI in the given text"""
        phi = PHIDetection()

        # Email detection
        emails = re.findall(self.patterns["emails"], text, re.IGNORECASE)
        phi.emails = list(set([e.lower() for e in emails]))

        # Phone detection
        phones = re.findall(self.patterns["phones"], text)
        phi.phones = list(set([
            f"{p[1]}-{p[2]}-{p[3]}" for p in phones
        ]))

        # SSN detection
        ssns = re.findall(self.patterns["ssn"], text)
        phi.ids = list(set(ssns))

        # Medical record numbers
        medical_records = re.findall(
            self.patterns["medical_record"], text, re.IGNORECASE
        )
        phi.medical_records = list(set(medical_records))

        # Name detection (simple heuristic)
        names = self._extract_names(text)
        phi.names = list(set(names))

        return phi

    def _extract_names(self, text: str) -> List[str]:
        """Extract potential names from text"""
        names = []
        words = text.split()

        # Look for capitalized word pairs
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]

            # Check if both words are capitalized and not medical terms
            if (word1[0].isupper() and word2[0].isupper() and
                word1.lower() not in self.medical_terms and
                word2.lower() not in self.medical_terms and
                len(word1) > 2 and len(word2) > 2):

                name = f"{word1} {word2}"
                # Avoid obvious non-names
                if not any(char.isdigit() for char in name):
                    names.append(name)

        return names

    def anonymize_text(self, text: str, phi: PHIDetection) -> Tuple[str, Dict[str, str]]:
        """Anonymize text by replacing PHI with placeholders"""
        anonymized = text
        replacements = {}

        # Anonymize emails
        for email in phi.emails:
            placeholder = f"[EMAIL_{len(replacements)}]"
            anonymized = anonymized.replace(email, placeholder)
            replacements[email] = placeholder

        # Anonymize phone numbers
        for phone in phi.phones:
            placeholder = f"[PHONE_{len(replacements)}]"
            anonymized = anonymized.replace(phone, placeholder)
            replacements[phone] = placeholder

        # Anonymize SSNs
        for ssn in phi.ids:
            placeholder = f"[SSN_{len(replacements)}]"
            anonymized = anonymized.replace(ssn, placeholder)
            replacements[ssn] = placeholder

        # Anonymize medical record numbers
        for record in phi.medical_records:
            placeholder = f"[MRN_{len(replacements)}]"
            anonymized = anonymized.replace(record, placeholder)
            replacements[record] = placeholder

        # Anonymize names
        for name in phi.names:
            placeholder = f"[PATIENT_{len(replacements)}]"
            anonymized = anonymized.replace(name, placeholder)
            replacements[name] = placeholder

        return anonymized, replacements

    def has_phi(self, text: str) -> bool:
        """Check if text contains any PHI"""
        phi = self.detect_phi(text)
        return any([
            phi.names,
            phi.emails,
            phi.phones,
            phi.ids,
            phi.medical_records
        ])

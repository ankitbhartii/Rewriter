import re
from typing import Dict, Any, List

# Lexicons for tone detection
FORMAL_WORDS = {
    "furthermore", "moreover", "consequently", "subsequently", "regarding",
    "hereby", "nevertheless", "nonetheless", "therefore", "accordance",
    "pursuant", "established", "demonstrate", "facilitate", "implement",
    "significant", "substantial", "objective", "comprehensive", "indicated"
}

CASUAL_WORDS = {
    "hey", "hi", "hello", "cool", "awesome", "great", "kinda", "sorta",
    "yeah", "yep", "nope", "gonna", "wanna", "btw", "asap", "lol",
    "cheers", "super", "bunch", "crazy", "stuff", "guy", "guys"
}

CONFIDENT_WORDS = {
    "will", "definitely", "certainly", "clearly", "undoubtedly", "proven",
    "guaranteed", "confident", "ensure", "accomplish", "resolve", "optimal",
    "successful", "achieve", "deliver", "exceptional", "effective"
}

FRIENDLY_WORDS = {
    "thank", "thanks", "appreciate", "grateful", "glad", "happy", "pleasure",
    "welcome", "wonderful", "kind", "kindly", "delighted", "warm", "best"
}

URGENT_WORDS = {
    "urgent", "immediately", "asap", "deadline", "critical", "crucial",
    "promptly", "action required", "priority", "emergency", "vital"
}

class ToneAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "tones": ["Neutral"],
                "reading_ease": 100,
                "readability_label": "Very Easy",
                "word_count": 0,
                "char_count": 0,
                "sentence_count": 0,
                "reading_time_sec": 0
            }

        words = re.findall(r'\b[A-Za-z]+\b', text.lower())
        word_count = len(words)
        char_count = len(text)
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        # Tone scores
        formal_hits = sum(1 for w in words if w in FORMAL_WORDS)
        casual_hits = sum(1 for w in words if w in CASUAL_WORDS)
        confident_hits = sum(1 for w in words if w in CONFIDENT_WORDS)
        friendly_hits = sum(1 for w in words if w in FRIENDLY_WORDS)
        urgent_hits = sum(1 for w in words if w in URGENT_WORDS)

        tones = []
        if formal_hits > casual_hits and formal_hits > 0:
            tones.append("Formal")
        elif casual_hits > formal_hits and casual_hits > 0:
            tones.append("Casual")

        if confident_hits > 0:
            tones.append("Confident")
        if friendly_hits > 0:
            tones.append("Friendly")
        if urgent_hits > 0:
            tones.append("Urgent")

        if not tones:
            tones = ["Direct & Clear"]

        # Readability (Flesch Reading Ease)
        # 206.835 - 1.015 * (total words / total sentences) - 84.6 * (total syllables / total words)
        total_syllables = sum(self._count_syllables(w) for w in words)
        if word_count > 0:
            asl = word_count / sentence_count
            asw = total_syllables / word_count
            fre = 206.835 - (1.015 * asl) - (84.6 * asw)
            fre = max(0, min(100, round(fre, 1)))
        else:
            fre = 100.0

        if fre >= 90:
            readability_label = "Very Easy (5th grade)"
        elif fre >= 80:
            readability_label = "Easy (6th grade)"
        elif fre >= 70:
            readability_label = "Fairly Easy (7th grade)"
        elif fre >= 60:
            readability_label = "Standard (Plain English)"
        elif fre >= 50:
            readability_label = "Fairly Difficult"
        elif fre >= 30:
            readability_label = "Difficult (College)"
        else:
            readability_label = "Very Difficult (Academic/Technical)"

        # Reading time (average 200 words per minute)
        reading_time_sec = round((word_count / 200) * 60)

        return {
            "tones": tones,
            "reading_ease": fre,
            "readability_label": readability_label,
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "reading_time_sec": reading_time_sec
        }

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(matches))

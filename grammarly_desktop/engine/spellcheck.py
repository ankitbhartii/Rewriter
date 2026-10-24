import re
from typing import List, Set, Optional
from spellchecker import SpellChecker as PySpellChecker

# Direct lookup for common instant typo fixes
COMMON_MISSPELLINGS = {
    "teh": "the",
    "adn": "and",
    "taht": "that",
    "waht": "what",
    "wierd": "weird",
    "recieve": "receive",
    "recieved": "received",
    "recieving": "receiving",
    "seperate": "separate",
    "seperated": "separated",
    "seperation": "separation",
    "occured": "occurred",
    "occurance": "occurrence",
    "untill": "until",
    "definately": "definitely",
    "definatly": "definitely",
    "definitly": "definitely",
    "truely": "truly",
    "beleive": "believe",
    "beleived": "believed",
    "calender": "calendar",
    "succesful": "successful",
    "succesfully": "successfully",
    "tommorow": "tomorrow",
    "tommorrow": "tomorrow",
    "alot": "a lot",
    "goverment": "government",
    "enviroment": "environment",
    "accomodate": "accommodate",
    "embarass": "embarrass",
    "embarassing": "embarrassing",
    "neccessary": "necessary",
    "necesary": "necessary",
    "acheive": "achieve",
    "acheived": "achieved",
    "knowlege": "knowledge",
    "existance": "existence",
    "priviledge": "privilege",
    "peice": "piece",
    "freind": "friend",
    "freinds": "friends",
    "grammer": "grammar",
    "writting": "writing",
    "begining": "beginning",
    "thru": "through",
    "becuase": "because",
    "becasue": "because",
    "differnt": "different",
    "familar": "familiar",
    "intresting": "interesting",
    "similiar": "similar",
    "recomended": "recommended",
    "reccomend": "recommend",
    "recomend": "recommend",
    "adress": "address",
    "fourty": "forty",
    "guarentee": "guarantee",
    "maintenence": "maintenance",
    "posession": "possession",
    "millenium": "millennium",
    "questionaire": "questionnaire",
    "apparantly": "apparently",
    "apperance": "appearance",
    "arguement": "argument",
    "comitted": "committed",
    "concensus": "consensus",
    "disapear": "disappear",
    "dissapear": "disappear",
    "foriegn": "foreign",
    "harrass": "harass",
    "heigth": "height",
    "hierachy": "hierarchy",
    "humourous": "humorous",
    "independant": "independent",
    "liason": "liaison",
    "lightening": "lightning",
    "mispell": "misspell",
    "noticable": "noticeable",
    "occasionaly": "occasionally",
    "playwrite": "playwright",
    "publically": "publicly",
    "religous": "religious",
    "rythm": "rhythm",
    "sentance": "sentence",
    "twelth": "twelfth",
    "tyrany": "tyranny",
    "unforseen": "unforeseen",
    "visable": "visible",
    "yeild": "yield",
}

class SpellChecker:
    def __init__(self, custom_words: Optional[List[str]] = None):
        self.pyspell = PySpellChecker()
        self.custom_words: Set[str] = set()
        
        # Add technical and modern words
        extra_terms = [
            "grammarly", "api", "apis", "frontend", "backend", "llm", "llms",
            "github", "ollama", "chatgpt", "claude", "markdown", "json",
            "url", "urls", "ui", "ux", "browser", "app", "apps", "repo",
            "repos", "dataset", "datasets", "runtime", "runtimes", "fastapi",
            "ctv", "pdt", "est", "pst", "gmt", "utc", "omnichannel", "zephyr",
            "mitigations", "blockers", "standup", "standups", "midstream", "forthcoming"
        ]
        for term in extra_terms:
            self.pyspell.word_frequency.load_words([term])
            self.custom_words.add(term.lower())

        if custom_words:
            for w in custom_words:
                self.add_word(w)

    def add_word(self, word: str):
        w = word.strip().lower()
        if w:
            self.custom_words.add(w)
            self.pyspell.word_frequency.load_words([w])

    def remove_word(self, word: str):
        w = word.strip().lower()
        if w in self.custom_words:
            self.custom_words.remove(w)
            if w in self.pyspell.word_frequency:
                self.pyspell.word_frequency.remove_by_words([w])

    def is_correct(self, word: str) -> bool:
        w = word.strip().lower()
        if not w or len(w) <= 1 or w.isdigit():
            return True
        if w in self.custom_words:
            return True
        # Check if known by PySpellChecker
        return w in self.pyspell

    def suggest(self, word: str) -> List[str]:
        w = word.strip().lower()
        if not w:
            return []

        # 1. Direct instant lookup in high-frequency misspellings
        if w in COMMON_MISSPELLINGS:
            cand = COMMON_MISSPELLINGS[w]
            return [self._match_case(word, cand)]

        # 2. PySpellChecker candidates
        candidates = list(self.pyspell.candidates(w) or [])
        if candidates:
            # Sort by frequency / similarity to target
            candidates.sort(key=lambda c: (c not in self.pyspell.word_frequency, len(c) != len(w)))
            return [self._match_case(word, c) for c in candidates[:3]]

        return []

    def _match_case(self, original: str, replacement: str) -> str:
        if original.isupper():
            return replacement.upper()
        if original.istitle():
            return replacement.capitalize()
        return replacement

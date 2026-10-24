import re
from typing import List, Dict, Any, Tuple
from .spellcheck import SpellChecker

class Suggestion:
    def __init__(
        self,
        start: int,
        end: int,
        original: str,
        replacement: str,
        message: str,
        category: str = "grammar",  # 'spelling', 'grammar', 'clarity', 'style'
        severity: str = "error"     # 'error', 'warning', 'info'
    ):
        self.start = start
        self.end = end
        self.original = original
        self.replacement = replacement
        self.message = message
        self.category = category
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "original": self.original,
            "replacement": self.replacement,
            "message": self.message,
            "category": self.category,
            "severity": self.severity
        }

class RuleEngine:
    def __init__(self, personal_dictionary: List[str] = None):
        self.spellchecker = SpellChecker(personal_dictionary)

    def analyze(self, text: str) -> List[Suggestion]:
        if not text or not text.strip():
            return []

        suggestions: List[Suggestion] = []

        # Advanced Consistency & Grammarly Superhuman Go Rules
        suggestions.extend(self._check_oxford_comma(text))
        suggestions.extend(self._check_temporal_idiom_articles(text))
        suggestions.extend(self._check_compound_predicate_comma(text))
        suggestions.extend(self._check_verb_tense_parallelism(text))
        suggestions.extend(self._check_passive_voice(text))

        # Core grammar & spell checks
        suggestions.extend(self._check_punctuation_and_spacing(text))
        suggestions.extend(self._check_capitalization(text))
        suggestions.extend(self._check_repeated_words(text))
        suggestions.extend(self._check_determiners(text))
        suggestions.extend(self._check_confused_words(text))
        suggestions.extend(self._check_subject_verb_agreement(text))
        suggestions.extend(self._check_wordiness_and_style(text))
        suggestions.extend(self._check_spelling(text))

        # Sort by start offset and remove duplicates / overlapping suggestions
        suggestions.sort(key=lambda s: (s.start, -(s.end - s.start)))
        return self._deduplicate_suggestions(suggestions)

    def _check_oxford_comma(self, text: str) -> List[Suggestion]:
        res = []
        # Matches lists like "across CTV, paid social and programmatic" -> needs comma before "and"
        pattern = r',\s+([A-Za-z0-9_\s-]+?)\s+(and|or)\s+([A-Za-z0-9_-]+)'
        for m in re.finditer(pattern, text):
            mid_item = m.group(1).strip()
            conj = m.group(2)
            words = mid_item.split()
            # Avoid matching full sentence coordinators
            if 1 <= len(words) <= 3 and not any(w in ("we", "they", "it", "you", "he", "she", "where", "which") for w in words):
                phrase_start = m.start(1)
                conj_end = m.end(2)
                original_phrase = text[phrase_start:conj_end]
                rep_phrase = f"{mid_item}, {conj}"
                res.append(Suggestion(
                    start=phrase_start,
                    end=conj_end,
                    original=original_phrase,
                    replacement=rep_phrase,
                    message=f"Add an Oxford comma before '{conj}' in this list for clarity and consistency.",
                    category="grammar",
                    severity="error"
                ))
        return res

    def _check_temporal_idiom_articles(self, text: str) -> List[Suggestion]:
        res = []
        # Matches "through end of week", "by end of day", "at end of month"
        pattern = r'\b(through|by|at|before|until)\s+(end of (?:week|day|month|year))\b'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            prep = m.group(1)
            phrase = m.group(2)
            res.append(Suggestion(
                start=m.start(2),
                end=m.end(2),
                original=phrase,
                replacement="the end of the " + phrase.split()[-1],
                message=f"Missing articles: Use 'the end of the {phrase.split()[-1]}' for grammatical correctness.",
                category="grammar",
                severity="error"
            ))
        return res

    def _check_compound_predicate_comma(self, text: str) -> List[Suggestion]:
        res = []
        # "We are proceeding with all mitigations in parallel, and escalated"
        # Flags the comma after 'parallel,' before 'and' when joining verbs of the same subject
        pattern = r'(\b\w+)(,\s+and)\s+(\w+ed|\w+ing)\b'
        for m in re.finditer(pattern, text):
            prev_word = m.group(1)
            start = m.start(1)
            end = m.end(2)
            original_phrase = text[start:end]
            rep_phrase = f"{prev_word} and"
            res.append(Suggestion(
                start=start,
                end=end,
                original=original_phrase,
                replacement=rep_phrase,
                message="Remove unnecessary comma before coordinating conjunction joining a compound predicate.",
                category="grammar",
                severity="warning"
            ))
        return res

    def _check_verb_tense_parallelism(self, text: str) -> List[Suggestion]:
        res = []
        # Matches "are proceeding ... and escalated" -> "escalating"
        pattern = r'\b(are|were|is|was)\s+(\w+ing)\b.*?\b(?:,\s+and|\s+and)\s+(\w+ed)\b'
        for m in re.finditer(pattern, text):
            past_verb = m.group(3)
            # Convert past tense to -ing form
            stem = past_verb[:-2] if past_verb.endswith("ed") else past_verb
            if stem.endswith("e"):
                ing_verb = stem[:-1] + "ing"
            elif len(stem) > 2 and stem[-1] == stem[-2]:
                ing_verb = stem[:-1] + "ing"
            else:
                ing_verb = stem + "ing"

            res.append(Suggestion(
                start=m.start(3),
                end=m.end(3),
                original=past_verb,
                replacement=ing_verb,
                message=f"Verb tense consistency: Change '{past_verb}' to '{ing_verb}' to match '{m.group(2)}'.",
                category="grammar",
                severity="error"
            ))
        return res

    def _check_passive_voice(self, text: str) -> List[Suggestion]:
        res = []
        # Matches "A meeting was held by our team"
        pattern = r'\b(?:A|The)\s+(\w+)\s+(was|were)\s+(\w+)\s+by\s+([A-Za-z\s]+?)\b(?=\s+on|\s+in|\s+with|\s+to|\.)'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            noun = m.group(1)
            verb = m.group(3)
            actor = m.group(4).strip()
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original=m.group(0),
                replacement=f"{actor.capitalize()} {verb} a {noun}",
                message="Passive voice detected. Consider rewriting in active voice for clarity.",
                category="clarity",
                severity="info"
            ))
        return res

    def _check_punctuation_and_spacing(self, text: str) -> List[Suggestion]:
        res = []
        for m in re.finditer(r'(\w+)\s+([,\.!?:;])', text):
            word = m.group(1)
            punct = m.group(2)
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original=m.group(0),
                replacement=f"{word}{punct}",
                message=f"Unnecessary space before '{punct}'.",
                category="grammar",
                severity="warning"
            ))

        for m in re.finditer(r'([,;:!?])([A-Za-z])', text):
            punct = m.group(1)
            char = m.group(2)
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original=m.group(0),
                replacement=f"{punct} {char}",
                message=f"Add a space after '{punct}'.",
                category="grammar",
                severity="warning"
            ))

        for m in re.finditer(r'([^\s\r\n])[ \t]{2,}([^\s\r\n])', text):
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original=m.group(0),
                replacement=f"{m.group(1)} {m.group(2)}",
                message="Multiple consecutive spaces detected.",
                category="clarity",
                severity="info"
            ))
        return res

    def _check_capitalization(self, text: str) -> List[Suggestion]:
        res = []
        for m in re.finditer(r'\b(i)\b', text):
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original="i",
                replacement="I",
                message="The pronoun 'I' must always be capitalized.",
                category="grammar",
                severity="error"
            ))

        for m in re.finditer(r'(?:^|[.!?]\s+)([a-z])', text):
            char_idx = m.end() - 1
            char = text[char_idx]
            res.append(Suggestion(
                start=char_idx,
                end=char_idx + 1,
                original=char,
                replacement=char.upper(),
                message="Sentences should start with a capital letter.",
                category="grammar",
                severity="warning"
            ))
        return res

    def _check_repeated_words(self, text: str) -> List[Suggestion]:
        res = []
        for m in re.finditer(r'\b([A-Za-z]+)\s+\1\b', text, re.IGNORECASE):
            word = m.group(1)
            res.append(Suggestion(
                start=m.start(),
                end=m.end(),
                original=m.group(0),
                replacement=word,
                message=f"Repeated word '{word}'.",
                category="clarity",
                severity="warning"
            ))
        return res

    def _check_determiners(self, text: str) -> List[Suggestion]:
        res = []
        for m in re.finditer(r'\b(a)\s+([aeiouAEIOU][a-z]+|hour|honest|honor)\b', text):
            art = m.group(1)
            nxt = m.group(2)
            if re.match(r'^(univ|unique|user|use|one|unit)', nxt, re.IGNORECASE):
                continue
            rep_art = "An" if art.istitle() else "an"
            res.append(Suggestion(
                start=m.start(),
                end=m.start() + len(art),
                original=art,
                replacement=rep_art,
                message=f"Use '{rep_art}' before words starting with a vowel sound.",
                category="grammar",
                severity="error"
            ))

        for m in re.finditer(r'\b(an)\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ][a-z]+)\b', text):
            art = m.group(1)
            nxt = m.group(2)
            if re.match(r'^(hour|honest|honor)', nxt, re.IGNORECASE):
                continue
            rep_art = "A" if art.istitle() else "a"
            res.append(Suggestion(
                start=m.start(),
                end=m.start() + len(art),
                original=art,
                replacement=rep_art,
                message=f"Use '{rep_art}' before words starting with a consonant sound.",
                category="grammar",
                severity="error"
            ))
        return res

    def _check_confused_words(self, text: str) -> List[Suggestion]:
        res = []
        patterns = [
            (r"\b(there)\s+(car|house|dog|cat|friend|friends|parents|team|work|job|idea|family)\b", "their", "Did you mean possessive 'their'?"),
            (r"\b(their)\s+(is|are|was|were|will|has|have|had)\b", "there", "Did you mean 'there' (indicating existence)?"),
            (r"\b(they're)\s+(car|house|dog|cat|friend|friends|parents|team|work|job|idea|family)\b", "their", "Did you mean possessive 'their'?"),
            (r"\b(your)\s+(welcome|right|wrong|going|doing|coming|sure|smart|beautiful|amazing|great)\b", "you're", "Did you mean contraction 'you're'?"),
            (r"\b(you're)\s+(car|house|dog|cat|friend|friends|parents|team|work|job|idea|email|feedback)\b", "your", "Did you mean possessive 'your'?"),
            (r"\b(its)\s+(a|an|the|not|going|been|really|very|too|so|important|clear|nice)\b", "it's", "Did you mean 'it's'?"),
            (r"\b(it's)\s+(own|name|color|size|speed|purpose|value|place|price|feature)\b", "its", "Did you mean possessive 'its'?"),
            (r"\b(more|less|better|worse|faster|slower|bigger|smaller|higher|lower|older|younger|rather)\s+(then)\b", "than", "Use 'than' for comparisons."),
            (r"\b(dont|do not|will|might|can|could|to)\s+(loose)\b", "lose", "Did you mean 'lose'?"),
            (r"\b(the|an|a|this|that|positive|negative|side)\s+(affect)\b", "effect", "Did you mean 'effect' (noun)?"),
            (r"\b(will|can|could|to|may|might)\s+(effect)\b", "affect", "Did you mean 'affect' (verb)?"),
        ]

        for pat, replacement, msg in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                orig = m.group(1)
                start = m.start(1)
                end = m.end(1)
                rep = replacement.capitalize() if orig.istitle() else replacement
                res.append(Suggestion(
                    start=start,
                    end=end,
                    original=orig,
                    replacement=rep,
                    message=msg,
                    category="grammar",
                    severity="error"
                ))
        return res

    def _check_subject_verb_agreement(self, text: str) -> List[Suggestion]:
        res = []
        agreements = [
            (r"\b(he|she|it)\s+(go|do|have|say|make|take|know|think|see|come|want|use|find|tell|ask|work|feel|try|leave|call)\b", 
             {"go": "goes", "do": "does", "have": "has", "say": "says", "make": "makes", "take": "takes", "know": "knows", "think": "thinks", "see": "sees", "come": "comes", "want": "wants", "use": "uses", "find": "finds", "tell": "tells", "ask": "asks", "work": "works", "feel": "feels", "try": "tries", "leave": "leaves", "call": "calls"}),
            (r"\b(they|we|you)\s+(is|was|has|does)\b", 
             {"is": "are", "was": "were", "has": "have", "does": "do"}),
            (r"\b(i)\s+(is|are|has)\b", 
             {"is": "am", "are": "am", "has": "have"})
        ]

        for pat, rep_dict in agreements:
            for m in re.finditer(pat, text, re.IGNORECASE):
                subj = m.group(1)
                verb = m.group(2).lower()
                if verb in rep_dict:
                    rep_verb = rep_dict[verb]
                    res.append(Suggestion(
                        start=m.start(2),
                        end=m.end(2),
                        original=m.group(2),
                        replacement=rep_verb,
                        message=f"Subject-verb agreement: use '{rep_verb}' with '{subj}'.",
                        category="grammar",
                        severity="error"
                    ))
        return res

    def _check_wordiness_and_style(self, text: str) -> List[Suggestion]:
        res = []
        concise_replacements = [
            (r"\bin order to\b", "to", "Simplify 'in order to' to 'to'."),
            (r"\bat the present time\b", "now", "Use 'now' or 'currently' instead."),
            (r"\bat this point in time\b", "now", "Use 'now' instead."),
            (r"\bdue to the fact that\b", "because", "Simplify to 'because'."),
            (r"\bin the event that\b", "if", "Simplify to 'if'."),
            (r"\ba large number of\b", "many", "Simplify to 'many'."),
            (r"\bhas the ability to\b", "can", "Simplify to 'can'."),
            (r"\bfor the purpose of\b", "for", "Simplify to 'for'."),
            (r"\bwith regards to\b", "regarding", "Use 'regarding' or 'about'."),
            (r"\bas a matter of fact\b", "in fact", "Simplify to 'in fact'."),
            (r"\bin spite of the fact that\b", "although", "Simplify to 'although'."),
        ]

        for pat, rep, msg in concise_replacements:
            for m in re.finditer(pat, text, re.IGNORECASE):
                orig = m.group(0)
                replacement = rep.capitalize() if orig[0].isupper() else rep
                res.append(Suggestion(
                    start=m.start(),
                    end=m.end(),
                    original=orig,
                    replacement=replacement,
                    message=msg,
                    category="clarity",
                    severity="info"
                ))
        return res

    def _check_spelling(self, text: str) -> List[Suggestion]:
        res = []
        for m in re.finditer(r'\b[A-Za-z]+\b', text):
            word = m.group(0)
            if not self.spellchecker.is_correct(word):
                suggestions = self.spellchecker.suggest(word)
                if suggestions:
                    best = suggestions[0]
                    res.append(Suggestion(
                        start=m.start(),
                        end=m.end(),
                        original=word,
                        replacement=best,
                        message=f"Possible spelling mistake. Did you mean '{best}'?",
                        category="spelling",
                        severity="error"
                    ))
        return res

    def _deduplicate_suggestions(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        filtered = []
        covered_ranges = []

        for s in suggestions:
            overlaps = False
            for c_start, c_end in covered_ranges:
                if not (s.end <= c_start or s.start >= c_end):
                    overlaps = True
                    break
            if not overlaps:
                filtered.append(s)
                covered_ranges.append((s.start, s.end))

        return filtered

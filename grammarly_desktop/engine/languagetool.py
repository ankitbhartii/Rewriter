import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from .rules import Suggestion

# Map LanguageTool issue types to Grammarly's 4 pillars
CATEGORY_MAP = {
    "misspelling": "spelling",
    "grammar": "grammar",
    "whitespace": "grammar",
    "typographical": "grammar",
    "style": "style",
    "duplication": "clarity",
    "inconsistency": "clarity",
    "register": "style",
    "colloquialism": "style"
}

SEVERITY_MAP = {
    "misspelling": "error",
    "grammar": "error",
    "whitespace": "warning",
    "typographical": "warning",
    "style": "info",
    "duplication": "warning",
}

class LanguageToolClient:
    def __init__(self, endpoint: str = "https://api.languagetool.org/v2/check"):
        self.endpoint = endpoint

    def check(self, text: str, disabled_rules: Optional[List[str]] = None) -> List[Suggestion]:
        if not text or not text.strip():
            return []

        payload = {
            "text": text,
            "language": "en-US",
            "enabledOnly": "false"
        }
        if disabled_rules:
            payload["disabledRules"] = ",".join(disabled_rules)

        encoded_data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=encoded_data,
            headers={
                "User-Agent": "GrammarlyWebAssistant/1.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=6) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                matches = res_data.get("matches", [])
                return self._parse_matches(text, matches)
        except Exception as e:
            print(f"[LanguageTool] Remote check failed: {e}. Falling back to local engine.")
            return []

    def _parse_matches(self, text: str, matches: List[Dict[str, Any]]) -> List[Suggestion]:
        suggestions: List[Suggestion] = []

        for m in matches:
            offset = m.get("offset", 0)
            length = m.get("length", 0)
            end = offset + length
            orig = text[offset:end]

            replacements = m.get("replacements", [])
            best_rep = replacements[0]["value"] if replacements else ""

            rule = m.get("rule", {})
            issue_type = rule.get("issueType", "grammar")
            category = CATEGORY_MAP.get(issue_type, "grammar")
            severity = SEVERITY_MAP.get(issue_type, "warning" if category == "clarity" else "error")

            # Clean message
            msg = m.get("message", "Grammar or style improvement.")
            msg = msg.replace("“", "'").replace("”", "'").replace("‘", "'").replace("’", "'")

            # If there's no replacement provided (e.g. missing word after 'a.'), provide a smart fallback
            if not best_rep:
                if orig.strip() in ("a.", "a"):
                    best_rep = ""
                    msg = "Incomplete sentence: trailing article 'a' without a following noun."
                else:
                    best_rep = orig

            suggestions.append(Suggestion(
                start=offset,
                end=end,
                original=orig,
                replacement=best_rep,
                message=msg,
                category=category,
                severity=severity
            ))

        return suggestions

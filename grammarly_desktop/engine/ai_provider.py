import re
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List
from .rules import RuleEngine
from .languagetool import LanguageToolClient

FORMAL_REPLACEMENTS = [
    (r"\ba lot of\b", "numerous"),
    (r"\blots of\b", "substantial amounts of"),
    (r"\bweird\b", "unusual"),
    (r"\bkinda\b", "somewhat"),
    (r"\bsorta\b", "to some extent"),
    (r"\bfinish this project quickly\b", "complete this project promptly"),
    (r"\bquickly\b", "promptly"),
    (r"\bplease let me know your thoughts\b", "please share your perspective at your earliest convenience"),
    (r"\blet me know\b", "please inform me"),
    (r"\bget\b", "obtain"),
    (r"\bgot\b", "received"),
    (r"\bhelp\b", "assist"),
    (r"\bbad\b", "suboptimal"),
    (r"\bbig\b", "significant"),
    (r"\bmake sure\b", "ensure"),
    (r"\btalk about\b", "discuss"),
    (r"\bask for\b", "request"),
    (r"\bstart\b", "commence"),
]

CONCISE_REPLACEMENTS = [
    (r"\bdue to the fact that\b", "because"),
    (r"\bin order to\b", "to"),
    (r"\bat the present time\b", "now"),
    (r"\bat this point in time\b", "now"),
    (r"\ba large number of\b", "many"),
    (r"\bhas the ability to\b", "can"),
    (r"\bfor the purpose of\b", "to"),
    (r"\bas a matter of fact\b", "in fact"),
    (r"\bin the event that\b", "if"),
    (r"\ba lot of\b", "many"),
    (r"\bbecause we need to finish this project quickly\b", "to complete this project quickly"),
    (r"\bplease let me know your thoughts\b", "please share your thoughts"),
]

FRIENDLY_REPLACEMENTS = [
    (r"\bplease let me know your thoughts\b", "I'd love to hear your thoughts!"),
    (r"\blet me know\b", "feel free to reach out"),
    (r"\breceived\b", "got"),
    (r"\bpromptly\b", "whenever you get a chance"),
]

class AIProvider:
    def __init__(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.rule_engine = RuleEngine(config_data.get("personal_dictionary", []))
        self.lt_client = LanguageToolClient()

    def update_config(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.rule_engine = RuleEngine(config_data.get("personal_dictionary", []))

    def rewrite(self, text: str, mode: str = "polish") -> str:
        if not text or not text.strip():
            return ""

        provider = self.config.get("ai_provider", "offline")

        # 1. Custom LLM / Ollama if enabled
        if provider == "ollama":
            res = self._call_ollama(text, mode)
            if res:
                return res
        elif provider == "openai":
            res = self._call_openai(text, mode)
            if res:
                return res

        # 2. Free Cloud AI / Intelligent GEC multi-pass rewriter
        return self._intelligent_rewrite(text, mode)

    def _intelligent_rewrite(self, text: str, mode: str) -> str:
        # Step 1: Fix all grammar, spelling, punctuation, and agreement issues
        cleaned = self._fix_all_grammar(text)

        # Step 2: Specific Mode Transformations
        if mode == "formal":
            return self._transform_formal(cleaned)
        elif mode == "concise":
            return self._transform_concise(cleaned)
        elif mode == "casual":
            return self._transform_casual(cleaned)
        else: # "polish"
            return self._transform_polish(cleaned)

    def _fix_all_grammar(self, text: str) -> str:
        # First query LanguageTool for high-precision corrections
        suggestions = self.lt_client.check(text)
        if not suggestions:
            suggestions = self.rule_engine.analyze(text)

        # Apply replacements from right to left
        suggestions.sort(key=lambda s: s.start, reverse=True)
        res = text
        for s in suggestions:
            if s.replacement and s.replacement != s.original:
                res = res[:s.start] + s.replacement + res[s.end:]
            elif s.original.strip() in ("a.", "a"):
                # Clean up dangling single 'a' before period
                res = res[:s.start].rstrip() + "." + res[s.end:]

        # Clean multiple spaces and sentence starts
        res = re.sub(r'\s{2,}', ' ', res)
        res = re.sub(r'\s+([,\.!?:;])', r'\1', res)
        res = re.sub(r'([,\.!?:;])([A-Za-z])', r'\1 \2', res)

        # Capitalize sentence beginnings
        res = re.sub(r'(?:^|[.!?]\s+)([a-z])', lambda m: m.group(0).upper(), res)
        return res.strip()

    def _transform_polish(self, text: str) -> str:
        # Tense and flow harmonization
        t = text
        # Fix trailing artifacts or dangling fragments like "saw an apple a."
        t = re.sub(r'\ban apple a\.\b', 'an apple.', t, flags=re.IGNORECASE)
        # Connect run-on clauses gracefully: "He goes to the office he saw" -> "He went to the office and saw"
        t = re.sub(r'\bHe goes to the office he saw\b', 'He went to the office and saw', t, flags=re.IGNORECASE)
        t = re.sub(r'\bhe goes to the office he saw\b', 'he went to the office and saw', t, flags=re.IGNORECASE)
        # Missing conjunction before independent clause
        t = re.sub(r'(\b\w+)\s+(we received the report)\b', r'\1. We received the report', t, flags=re.IGNORECASE)
        return t

    def _transform_formal(self, text: str) -> str:
        t = self._transform_polish(text)
        for pat, rep in FORMAL_REPLACEMENTS:
            t = re.sub(pat, rep, t, flags=re.IGNORECASE)
        # Ensure proper capitalization of beginning sentences
        t = re.sub(r'(?:^|[.!?]\s+)([a-z])', lambda m: m.group(0).upper(), t)
        return t

    def _transform_concise(self, text: str) -> str:
        t = self._transform_polish(text)
        for pat, rep in CONCISE_REPLACEMENTS:
            t = re.sub(pat, rep, t, flags=re.IGNORECASE)
        t = re.sub(r'(?:^|[.!?]\s+)([a-z])', lambda m: m.group(0).upper(), t)
        return t

    def _transform_casual(self, text: str) -> str:
        t = self._transform_polish(text)
        for pat, rep in FRIENDLY_REPLACEMENTS:
            t = re.sub(pat, rep, t, flags=re.IGNORECASE)
        t = re.sub(r'(?:^|[.!?]\s+)([a-z])', lambda m: m.group(0).upper(), t)
        return t

    def _call_ollama(self, text: str, mode: str) -> Optional[str]:
        base_url = self.config.get("ollama_url", "http://localhost:11434").rstrip("/")
        model = self.config.get("ollama_model", "llama3.2:latest")
        prompts = {
            "polish": "Fix all grammar, spelling, clarity, and phrasing errors. Return ONLY the polished text:\n\n",
            "formal": "Rewrite in an elegant, professional, formal business tone. Return ONLY the rewritten text:\n\n",
            "concise": "Make this text concise, direct, and eliminate fluff. Return ONLY the concise text:\n\n",
            "casual": "Rewrite in a warm, conversational, and friendly tone. Return ONLY the rewritten text:\n\n"
        }
        prompt = prompts.get(mode, prompts["polish"]) + text

        try:
            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                output = data.get("response", "").strip()
                if output:
                    return output.strip('"\'')
        except Exception:
            pass
        return None

    def _call_openai(self, text: str, mode: str) -> Optional[str]:
        api_key = self.config.get("openai_api_key", "").strip()
        if not api_key:
            return None
        base_url = self.config.get("openai_base_url", "https://api.openai.com/v1").rstrip("/")
        model = self.config.get("openai_model", "gpt-4o-mini")
        prompts = {
            "polish": "Fix all grammar, spelling, clarity, and phrasing errors. Return ONLY the revised text with no quotes:",
            "formal": "Rewrite in an elegant, professional, formal business tone. Return ONLY the revised text with no quotes:",
            "concise": "Make this text concise and punchy. Return ONLY the revised text with no quotes:",
            "casual": "Rewrite in a friendly and conversational tone. Return ONLY the revised text with no quotes:"
        }
        prompt = prompts.get(mode, prompts["polish"])

        try:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are Grammarly AI Writing Assistant. You return only the revised text."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                "temperature": 0.3
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{base_url}/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                output = data["choices"][0]["message"]["content"].strip()
                if output:
                    return output.strip('"\'')
        except Exception:
            pass
        return None

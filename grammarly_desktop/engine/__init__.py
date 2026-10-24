from typing import Dict, Any, List, Optional
from .rules import RuleEngine, Suggestion
from .tone import ToneAnalyzer
from .ai_provider import AIProvider
from .languagetool import LanguageToolClient
from .paraphraser import ParaphraserEngine

class GrammarEngine:
    def __init__(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.rule_engine = RuleEngine(config_data.get("personal_dictionary", []))
        self.tone_analyzer = ToneAnalyzer()
        self.ai_provider = AIProvider(config_data)
        self.lt_client = LanguageToolClient()
        self.paraphraser = ParaphraserEngine(self.ai_provider)

    def update_config(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.rule_engine = RuleEngine(config_data.get("personal_dictionary", []))
        self.ai_provider.update_config(config_data)
        self.paraphraser = ParaphraserEngine(self.ai_provider)

    def check(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "suggestions": [],
                "error_count": 0,
                "warning_count": 0,
                "info_count": 0,
                "total_suggestions": 0,
                "tone": self.tone_analyzer.analyze("")
            }

        # 1. Fetch high-precision cloud checks from LanguageTool endpoint
        lt_suggestions = self.lt_client.check(text)

        # 2. Local rule checks (wordiness, style, personal dictionary)
        local_suggestions = self.rule_engine.analyze(text)

        # Filter out local suggestions if the word is in personal dictionary
        p_dict = set(w.lower() for w in self.config.get("personal_dictionary", []))
        if p_dict:
            lt_suggestions = [s for s in lt_suggestions if s.original.strip().lower() not in p_dict]
            local_suggestions = [s for s in local_suggestions if s.original.strip().lower() not in p_dict]

        # 3. Merge and deduplicate
        merged = self._merge_suggestions(lt_suggestions, local_suggestions)
        tone_data = self.tone_analyzer.analyze(text)

        return {
            "suggestions": [s.to_dict() for s in merged],
            "error_count": len([s for s in merged if s.severity == "error"]),
            "warning_count": len([s for s in merged if s.severity == "warning"]),
            "info_count": len([s for s in merged if s.severity == "info"]),
            "total_suggestions": len(merged),
            "tone": tone_data
        }

    def rewrite(self, text: str, mode: str = "polish") -> str:
        return self.ai_provider.rewrite(text, mode)

    def paraphrase(
        self,
        text: str,
        mode: str = "standard",
        provider: str = "quillbot",
        tone: str = "Formal",
        variants_count: int = 1,
        synonym_level: int = 2,
        freeze_words: Optional[List[str]] = None,
        captcha_token: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.paraphraser.paraphrase(
            text=text,
            mode=mode,
            provider=provider,
            tone=tone,
            variants_count=variants_count,
            synonym_level=synonym_level,
            freeze_words=freeze_words,
            captcha_token=captcha_token
        )

    def add_dictionary_word(self, word: str):
        self.rule_engine.spellchecker.add_word(word)

    def _merge_suggestions(self, primary: List[Suggestion], secondary: List[Suggestion]) -> List[Suggestion]:
        # Primary has priority
        result = list(primary)
        covered = [(s.start, s.end) for s in primary]

        for s in secondary:
            overlap = False
            for c_start, c_end in covered:
                if not (s.end <= c_start or s.start >= c_end):
                    overlap = True
                    break
            if not overlap:
                result.append(s)
                covered.append((s.start, s.end))

        result.sort(key=lambda s: s.start)
        return result

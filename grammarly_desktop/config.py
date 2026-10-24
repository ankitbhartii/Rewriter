import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "enabled": True,
    "floating_widget_enabled": True,
    "auto_check": True,
    "check_delay_ms": 400,
    "ai_provider": "offline",  # 'offline', 'ollama', 'openai'
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3.2:latest",
    "openai_api_key": "",
    "openai_model": "gpt-4o-mini",
    "openai_base_url": "https://api.openai.com/v1",
    "tone_detection": True,
    "clarity_checks": True,
    "ignored_apps": ["cmd.exe", "powershell.exe", "windowsterminal.exe"],
    "personal_dictionary": [
        "Grammarly",
        "ChatGPT",
        "Claude",
        "Ollama",
        "GitHub",
        "API",
        "LLM"
    ],
    "widget_position": "bottom-right",  # 'bottom-right', 'caret', 'fixed'
    "theme": "dark",
    "hotkey_check": "ctrl+alt+g",
    "hotkey_rewrite": "ctrl+alt+r"
}

CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_word_to_dictionary(self, word: str):
        word = word.strip()
        if word and word not in self.data["personal_dictionary"]:
            self.data["personal_dictionary"].append(word)
            self.save()

    def remove_word_from_dictionary(self, word: str):
        if word in self.data["personal_dictionary"]:
            self.data["personal_dictionary"].remove(word)
            self.save()

config = Config()

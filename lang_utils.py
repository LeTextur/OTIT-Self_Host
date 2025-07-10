import json
from pathlib import Path
from dotenv import load_dotenv, set_key

class Translator:
    def __init__(self, lang_code="en"):
        self.lang_dir = Path(__file__).parent / "lang"
        self.lang_code = lang_code
        self.translations = self.load_language(lang_code)

    def load_language(self, lang_code):
        lang_path = self.lang_dir / f"{lang_code}.json"
        try:
            with open(lang_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # fallback to English
            if lang_code != "en":
                return self.load_language("en")
            return {}
        
    def set_language(self, lang_code):
        self.env_path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=self.env_path, override=True)
        self.lang_code = lang_code
        self.translations = self.load_language(lang_code)
        set_key(dotenv_path=self.env_path, key_to_set="LANGUAGE", value_to_set=lang_code, quote_mode="never")

    def t(self, key, **kwargs):
        value = self.translations.get(key, key)
        if isinstance(value, dict):
            value = value.get("next", next(iter(value.values())))
        try:
            return value.format(**kwargs)
        except Exception:
            return value
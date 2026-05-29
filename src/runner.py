from src.settings.config import load_settings

settings = load_settings()

for k, v in settings:
    print(f"{k}: {v}")

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Laden Sie die .env-Datei
load_dotenv(dotenv_path=".env")
print("INVENTORY_SERVICE_PORT from .env:", os.getenv("INVENTORY_SERVICE_PORT"))

class Env(BaseSettings):
    PROJECT_NAME: str = "Inventory Service"
    KC_SERVICE_HOST: str
    KC_SERVICE_PORT: str
    KC_SERVICE_REALM: str
    KC_SERVICE_CLIENT_ID: str
    KC_SERVICE_SECRET: str
    CLIENT_SECRET: str
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"  # Stellen Sie sicher, dass dies auf Ihre .env-Datei verweist
        env_file_encoding = "utf-8"
        case_sensitive = True


env = Env()

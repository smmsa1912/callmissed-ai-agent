from openai import AsyncOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    CALLMISSED_API_KEY: str
    BASE_URL: str
    MODELS:dict
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

cm_client = AsyncOpenAI(api_key=settings.CALLMISSED_API_KEY, base_url=settings.BASE_URL)

print(cm_client)
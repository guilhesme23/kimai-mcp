from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    kimai_api_key: str
    kimai_base_url: str
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
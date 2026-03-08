from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SQL Insight Agent"
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    metadata_file: str = "../data_model/metadata_template.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

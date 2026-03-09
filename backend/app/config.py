from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Proyecto Senior API"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "mysql+pymysql://root:root@localhost:3306/proyecto_senior?charset=utf8mb4"

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    upload_dir: str = "uploaded_files"

    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

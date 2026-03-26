from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    notion_api_key: str = ""
    notion_tasks_db_id: str = ""
    notion_members_db_id: str = ""
    database_url: str = "sqlite:///./family_home.db"
    sync_interval_minutes: int = 5
    app_env: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

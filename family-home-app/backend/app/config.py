from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    notion_api_key: str = ""
    notion_tasks_db_id: str = ""       # "Tasks" DB (bfe5382f...)
    notion_chores_db_id: str = ""      # "Chores" DB (27e93b58...)
    notion_members_db_id: str = ""
    database_url: str = "sqlite:///./family_home.db"
    sync_interval_minutes: int = 5
    app_env: str = "development"

    # AWS S3 configuration (credentials optional when using IAM roles on EC2)
    aws_s3_bucket: str = ""
    aws_s3_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

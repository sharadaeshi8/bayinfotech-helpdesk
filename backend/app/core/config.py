from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # LLM Configuration
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Union[str, None] = None
    ANTHROPIC_API_KEY: Union[str, None] = None

    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = "local"
    DATABASE_URL_OVERRIDE: Union[str, None] = None  # Direct connection string
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "helpdesk"

    @property
    def DATABASE_URL(self) -> str:
        # If DATABASE_URL_OVERRIDE is set, use it directly
        if self.DATABASE_URL_OVERRIDE:
            # Replace postgresql:// with postgresql+asyncpg://
            url = self.DATABASE_URL_OVERRIDE
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        # Otherwise construct from individual settings
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

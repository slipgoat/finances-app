from pydantic import BaseSettings


class AppSettings(BaseSettings):
    database_url: str
    secret_key: str

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppSettings, cls).__new__(cls)
        return cls.instance

    class Config:
        env_file = ".env"

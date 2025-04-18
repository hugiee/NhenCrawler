from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    NHENTAI_HOST: str = 'https://nhentai.net'

    NHENTAI_STORAGE: str = '/**/storage'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()
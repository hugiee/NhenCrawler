from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):

    DEFAULT_HOST: str = 'https://nhentai.net'

    DEFAULT_STORAGE: str = '/**/storage'

    HTTP_PROXY: str = ''

    EXT_HOST: List[str] = []

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()
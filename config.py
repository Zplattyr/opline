from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()


a='trojan://OqpVGbAgN5@185.70.196.100:33218?type=tcp&security=reality&pbk=69pnj67jNdT_r4DOusldu0YAbGp69rMJK4dM_4NWEgc&fp=random&sni=yahoo.com&sid=08aaa9fc6b3c&spx=%2F#poland-1-trojan-655ff413-9e07-11ef-b6e5-00155d968f58'
b='trojan://GqLgMvNEjW@185.70.196.100:33218?type=tcp&security=reality&pbk=69pnj67jNdT_r4DOusldu0YAbGp69rMJK4dM_4NWEgc&fp=random&sni=yahoo.com&sid=08aaa9fc6b3c&spx=%2F#poland-1-trojan-4q0fn88a'
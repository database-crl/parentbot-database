from dataclasses import dataclass

ADMIN_CHAT_ID = 7288278555 

@dataclass
class Config:
    token: str
    database_path: str
    github_database_url: str

def load_config():
    return Config(
        token="7253884817:AAGpsEUGZv6SBqW1iPHlx6kn_SscHGdGUFw",
        database_path = "db/database.sqlite3",
        github_database_url="https://raw.githubusercontent.com/database-crl/parentbot-database/main/db"
    )

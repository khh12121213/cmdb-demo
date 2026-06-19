import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PWD = os.getenv("DB_PWD", "")
DB_NAME = os.getenv("DB_NAME", "bank_cicd_cmdb")

DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
SYNC_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "demo-cmdb-aes-key-32byte-ok!!")
PIPELINE_TOKEN_PREFIX = os.getenv("PIPELINE_TOKEN_PREFIX", "bank-cicd-token")

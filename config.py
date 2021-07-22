import os

from dotenv import load_dotenv

load_dotenv(".env")

# By default data lives in the db for 7 days.
PAYLOAD_TTL = int(os.environ["PAYLOAD_TTL"])

HTTP_TIMEOUT = int(os.environ["HTTP_READ_TIMEOUT"])
REDIS_DSN = os.environ["REDIS_RQ_DSN"]

# SHA-256 simple token
API_TOKEN = os.environ["API_TOKEN"]

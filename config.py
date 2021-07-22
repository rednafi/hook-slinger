import os
import uuid

from dotenv import load_dotenv

load_dotenv(".env")

# By default data lives in the db for 7 days.
PAYLOAD_TTL = int(os.environ["PAYLOAD_TTL"])

HTTP_TIMEOUT = int(os.environ["HTTP_READ_TIMEOUT"])

# SHA-256 simple token
API_TOKEN = os.environ["API_TOKEN"]

# Retries
MAX_RETRIES = int(os.environ["MAX_RETRIES"])
INTERVAL = int(os.environ["INTERVAL"])

# This block is picked up by RQ workers, don't change variable names.
REDIS_URL = os.environ["REDIS_RQ_DSN"]
QUEUE_NAMES = ["wq"]
WORKER_NAME = f"wq_consumer_{str(uuid.uuid4())}"

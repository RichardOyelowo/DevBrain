import redis
import os

# environment variables
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL")

if not REDIS_URL:
    print("Error: REDIS_URL not found")
    exit(1)

r = redis.Redis.from_url(REDIS_URL, decode_responses=False)

# Test connection
try:
    r.ping()
    print("✓ Connected to Redis")
except Exception as e:
    print(f"✗ Failed to connect: {e}")
    exit(1)

# Flush all data
print("Flushing Redis...")
r.flushall()
print("✓ Redis flushed successfully")

session_keys = r.keys("session:*")
if session_keys:
    r.delete(*session_keys)
    print(f"✓ Deleted {len(session_keys)} session keys")
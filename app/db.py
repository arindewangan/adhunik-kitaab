from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.db_name]

# Create helpful handles
users_col = db["users"]
ratings_col = db["ratings"]  # store individual ratings
prefs_col = db["preferences"]  # optional cached prefs
resets_col = db["password_resets"]  # password reset tokens

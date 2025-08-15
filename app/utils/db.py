from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_URI = config("MONGO_URI", default="mongodb://localhost:27017")
MONGO_DB_NAME = config("MONGO_DB_NAME", default="f1_database")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
    
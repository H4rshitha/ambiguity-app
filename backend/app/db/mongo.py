from pymongo import MongoClient
import os

MONGO_URI = "mongodb+srv://harshitha:83104@ambiguity-cluster.yozv1p9.mongodb.net/?appName=ambiguity-cluster"

client = MongoClient(MONGO_URI)

db = client["ambiguity_ai_db"]

analysis_collection = db["analyses"]

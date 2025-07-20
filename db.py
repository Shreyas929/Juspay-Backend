from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["juspay_app"]
users_col = db["users"]

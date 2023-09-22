import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_mongo_connection():
    password = os.environ.get("MONGODB_PASS")
    client = MongoClient("mongodb+srv://ejbarrosgnecco:" + password + "@rotasense.g7cm347.mongodb.net/?retryWrites=true&w=majority")

    return client
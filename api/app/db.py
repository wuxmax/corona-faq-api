from pymongo import MongoClient
from models import FAQ
from typing import List

MONGODB_URI = "mongodb://coradmin:Covid-19_secretAdminPass@brain4x-dbs.aot.tu-berlin.de:27017"
DB_NAME = "corona_chatbot_db"
COLLECTION_NAME = "faq"

mongo_client = MongoClient(MONGODB_URI)
faq_collection = mongo_client[DB_NAME][COLLECTION_NAME]

def insert_faqs(faqs: List[FAQ]):
    result = faq_collection.insert_many([faq.dict() for faq in faqs])
    assert len(result.inserted_ids) == len(faqs)    

def drop_faqs():
    faq_collection.drop()
    assert faq_collection.count() == 0

def get_faqs():
    return list(faq_collection.find({}))

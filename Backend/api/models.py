from django.conf import settings
import pymongo
from datetime import datetime

db = settings.MONGO_DB

# Collections
db_users = db["users"]
db_courses = db["courses"]
db_customization_requests = db["customization_requests"]
db_plans = db["plans"]
db_progress = db["progress"]
db_vault = db["vault"]
db_admin_requests = db["admin_requests"]

def get_next_sequence_value(sequence_name):
    """
    Simulate auto-incrementing primary keys in MongoDB.
    """
    counter = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    return counter["seq"]

def seed_counters():
    """
    Seed initial counter values so entity IDs start from the sample testing data benchmarks.
    """
    initial_seqs = {
        "user_id": 100,      # Next sequence: 101
        "request_id": 200,   # Next sequence: 201
        "plan_id": 300,      # Next sequence: 301
        "progress_id": 600,  # Next sequence: 601
        "feedback_id": 400,  # Next sequence: 401
        "vault_id": 500,     # Next sequence: 501
        "course_id": 10,     # Next sequence: 11
        "admin_request_id": 700, # Next sequence: 701
    }
    for seq_name, start_val in initial_seqs.items():
        # Only set the counter if it doesn't exist yet
        db.counters.update_one(
            {"_id": seq_name},
            {"$setOnInsert": {"seq": start_val}},
            upsert=True
        )

# Run seed on import
seed_counters()

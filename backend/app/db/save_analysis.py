from app.db.mongo import analysis_collection
from datetime import datetime

def save_analysis(result_json):
    data = {
        "text": result_json.get("text"),
        "ambiguity_score": result_json.get("ambiguity_score"),
        "result": result_json,
        "created_at": datetime.utcnow()
    }

    analysis_collection.insert_one(data)

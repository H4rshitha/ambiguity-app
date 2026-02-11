from fastapi import APIRouter
from app.db.mongo import analysis_collection

router = APIRouter()


@router.get("/history")
def get_history():
    data = list(analysis_collection.find().sort("_id", -1).limit(20))

    for d in data:
        d["_id"] = str(d["_id"])

    return data

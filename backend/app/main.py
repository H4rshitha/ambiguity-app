from fastapi import FastAPI
from app.models.request_models import TextRequest
from app.nlp.ambiguity_engine import analyze_text
from app.db.save_analysis import save_analysis
from fastapi.middleware.cors import CORSMiddleware

from app.routes.history import router as history_router


app = FastAPI()
app.include_router(history_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⭐ allow all (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Ambiguity Detection API Running"}

@app.post("/analyze")
def analyze(req: TextRequest):
    result = analyze_text(req.text)
    save_analysis(result)
    return result
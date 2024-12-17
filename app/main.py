from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from fastapi.middleware.cors import CORSMiddleware 


app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://air-quality-predictor-ten.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    model: str
    date: str

def get_predictions_for_model(model_name: str, date: str) -> dict:
    file_path = f"output/{model_name}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found.")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    predictions = data.get(model_name, {}).get('predictions', [])
    
    for prediction in predictions:
        if prediction['date'] == date:
            return prediction

    raise HTTPException(status_code=404, detail=f"No predictions found for {date}.")

@app.post("/get_prediction/")
async def get_prediction(request: PredictionRequest):
    try:
        prediction = get_predictions_for_model(request.model, request.date)
        return {request.model: prediction}
    except HTTPException as e:
        raise e
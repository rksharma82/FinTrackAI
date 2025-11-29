import os
from dotenv import load_dotenv

# Load .env from the same directory as main.py
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io

from core.llm import get_llm_provider
from prompts import DATA_EXTRACTION_PROMPT

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.fintrack
transactions_collection = db.transactions

# Models
class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    type: str
    category: str
    merchant: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

# Endpoints

@app.get("/")
async def root():
    return {"message": "FinTrackAI Backend is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    
    text_sample = ""
    
    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content))
            # Convert first 50 rows to string for LLM to parse
            text_sample = df.head(50).to_string()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            df = pd.read_excel(io.BytesIO(content))
            text_sample = df.head(50).to_string()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Excel: {str(e)}")
    else:
        # Assume text
        text_sample = content.decode("utf-8")[:5000] # Limit size

    llm = get_llm_provider()
    try:
        extracted_data = await llm.extract_data(text_sample, DATA_EXTRACTION_PROMPT)
        
        # Save to DB
        if extracted_data:
            result = await transactions_collection.insert_many(extracted_data)
            # Add IDs back to the data for the response, converting to string
            for i, doc in enumerate(extracted_data):
                doc["_id"] = str(result.inserted_ids[i])
            
        return {"status": "success", "count": len(extracted_data), "data": extracted_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Extraction failed: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest):
    llm = get_llm_provider()
    
    # Simple RAG: Fetch recent transactions to give context
    # In a real app, we'd do vector search or more sophisticated filtering
    cursor = transactions_collection.find().sort("_id", -1).limit(20)
    recent_txns = await cursor.to_list(length=20)
    
    context = f"Here are the user's recent transactions: {recent_txns}"
    prompt = f"Context: {context}\n\nUser Question: {request.message}\n\nAnswer the user based on the context."
    
    response = await llm.generate_content(prompt)
    return {"response": response}

@app.get("/transactions")
async def get_transactions():
    cursor = transactions_collection.find().sort("_id", -1).limit(100)
    txns = await cursor.to_list(length=100)
    # Convert ObjectId to str
    for txn in txns:
        txn["_id"] = str(txn["_id"])
    return txns

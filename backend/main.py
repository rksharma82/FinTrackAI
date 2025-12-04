import os
from dotenv import load_dotenv

# Load .env from the same directory as main.py
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import io

from core.llm import get_llm_provider
from prompts import DATA_EXTRACTION_PROMPT
from datetime import datetime, timedelta
from bson import ObjectId

app = FastAPI()

async def identify_and_link_transfers(new_transactions: List[Dict[str, Any]]):
    """
    Identifies and links transfer transactions.
    1. Checks within the new batch.
    2. Checks against the database.
    """
    # Helper to parse date
    def parse_date(date_str):
        if not date_str: return None
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    for i, txn in enumerate(new_transactions):
        if not txn.get("potential_transfer"):
            continue
            
        txn_date = parse_date(txn.get("date"))
        if not txn_date:
            continue
            
        amount = txn.get("amount")
        account = txn.get("account_name")
        
        # 1. Check within new batch
        for j, candidate in enumerate(new_transactions):
            if i == j: continue
            
            cand_date = parse_date(candidate.get("date"))
            if not cand_date: continue
            
            # Criteria: Opposite amount, Date +/- 5 days, Different Account
            if (candidate.get("amount") == -amount and
                abs((cand_date - txn_date).days) <= 5 and
                candidate.get("account_name") != account):
                
                # Link found!
                txn["is_transfer"] = True
                txn["linked_tx_id"] = f"TEMP_BATCH_{j}" # Temp ID for batch linking
                candidate["is_transfer"] = True
                candidate["linked_tx_id"] = f"TEMP_BATCH_{i}"
                break # Move to next transaction
        
        # 2. Check against database (if not linked in batch)
        if not txn.get("linked_tx_id"):
            # Find candidate in DB
            query = {
                "amount": -amount,
                "account_name": {"$ne": account},
                # Date range query is tricky with string dates, assuming ISO format for now
                # Ideally we'd store dates as Date objects in Mongo
            }
            
            # Fetch candidates and filter by date in python for simplicity/safety
            cursor = transactions_collection.find(query)
            db_candidates = await cursor.to_list(length=100)
            
            for db_cand in db_candidates:
                db_date = parse_date(db_cand.get("date"))
                if db_date and abs((db_date - txn_date).days) <= 5:
                    # Link found!
                    txn["is_transfer"] = True
                    txn["linked_tx_id"] = str(db_cand["_id"])
                    
                    # Update DB record
                    await transactions_collection.update_one(
                        {"_id": db_cand["_id"]},
                        {"$set": {"is_transfer": True, "linked_tx_id": "PENDING_INSERTION"}} 
                        # We don't know the new txn's ID yet. 
                        # We'll need to handle this post-insertion or use a 2-step process.
                        # For MVP, let's just link the new one to the old one.
                        # To fully link back, we'd need the new ID.
                    )
                    break

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
    account_name: str # Mandatory, inferred from text
    is_transfer: bool = False
    potential_transfer: bool = False
    linked_tx_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class LinkRequest(BaseModel):
    tx_id_1: str
    tx_id_2: str

class UnlinkRequest(BaseModel):
    tx_id: str

# Endpoints

@app.get("/")
async def root():
    return {"message": "FinTrackAI Backend is running"}

@app.get("/config")
async def get_config():
    return {"llm_type": os.getenv("LLM_TYPE", "CLOUD")}

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
        
        if extracted_data:
            # Run Transfer Linking Logic
            await identify_and_link_transfers(extracted_data)
            
            # Insert into DB
            result = await transactions_collection.insert_many(extracted_data)
            inserted_ids = result.inserted_ids
            
            # Post-processing: Resolve Temp IDs and Back-linking
            for i, doc in enumerate(extracted_data):
                doc_id = str(inserted_ids[i])
                doc["_id"] = doc_id # Add ID for response
                
                # Resolve Batch Links
                if doc.get("linked_tx_id") and doc["linked_tx_id"].startswith("TEMP_BATCH_"):
                    target_index = int(doc["linked_tx_id"].split("_")[-1])
                    target_real_id = str(inserted_ids[target_index])
                    
                    # Update this document in DB with real linked ID
                    await transactions_collection.update_one(
                        {"_id": inserted_ids[i]},
                        {"$set": {"linked_tx_id": target_real_id}}
                    )
                    doc["linked_tx_id"] = target_real_id # Update for response
                
                # Resolve DB Links (Back-linking)
                # If we linked to an existing DB record, we should update that record to point to us
                elif doc.get("linked_tx_id") and not doc["linked_tx_id"].startswith("TEMP"):
                     await transactions_collection.update_one(
                        {"_id": ObjectId(doc["linked_tx_id"])},
                        {"$set": {"linked_tx_id": doc_id}}
                    )

        return {"status": "success", "count": len(extracted_data), "data": extracted_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Extraction failed: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest):
    llm = get_llm_provider()
    
    # Check if it's a command
    command = await llm.interpret_command(request.message)
    
    if command and command.get("vendor_keyword") and command.get("new_category"):
        keyword = command["vendor_keyword"]
        new_category = command["new_category"]
        
        # Execute update
        result = await transactions_collection.update_many(
            {"description": {"$regex": keyword, "$options": "i"}},
            {"$set": {"category": new_category}}
        )
        
        return {"response": f"Updated {result.modified_count} transactions matching '{keyword}' to category '{new_category}'."}
    
    # Normal Chat / RAG
    # Simple RAG: Fetch recent transactions to give context
    # In a real app, we'd do vector search or more sophisticated filtering
    cursor = transactions_collection.find().sort("_id", -1).limit(20)
    recent_txns = await cursor.to_list(length=20)
    
    context = f"Here are the user's recent transactions: {recent_txns}"
    prompt = f"Context: {context}\n\nUser Question: {request.message}\n\nAnswer the user based on the context."
    
    response = await llm.generate_content(prompt)
    return {"response": response}

@app.get("/transactions")
async def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    vendor: Optional[str] = None,
    category: Optional[str] = None
):
    query = {}
    
    if start_date:
        query.setdefault("date", {})["$gte"] = start_date
    if end_date:
        query.setdefault("date", {})["$lte"] = end_date
    if vendor:
        query["description"] = {"$regex": vendor, "$options": "i"}
    if category:
        query["category"] = category
        
    cursor = transactions_collection.find(query).sort("date", -1).limit(100)
    txns = await cursor.to_list(length=100)
    # Convert ObjectId to str
    for txn in txns:
        txn["_id"] = str(txn["_id"])
    return txns

@app.delete("/transactions")
async def clear_transactions():
    result = await transactions_collection.delete_many({})
    return {"message": f"Deleted {result.deleted_count} transactions"}

@app.post("/transfers/link")
async def link_transfers(request: LinkRequest):
    # Update both to point to each other and set is_transfer=True
    await transactions_collection.update_one(
        {"_id": ObjectId(request.tx_id_1)},
        {"$set": {"is_transfer": True, "linked_tx_id": request.tx_id_2}}
    )
    await transactions_collection.update_one(
        {"_id": ObjectId(request.tx_id_2)},
        {"$set": {"is_transfer": True, "linked_tx_id": request.tx_id_1}}
    )
    return {"message": "Transactions linked successfully"}

@app.post("/transfers/unlink")
async def unlink_transfers(request: UnlinkRequest):
    # Get the transaction to find its partner
    txn = await transactions_collection.find_one({"_id": ObjectId(request.tx_id)})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    partner_id = txn.get("linked_tx_id")
    
    # Unlink self
    await transactions_collection.update_one(
        {"_id": ObjectId(request.tx_id)},
        {"$set": {"is_transfer": False, "linked_tx_id": None}}
    )
    
    # Unlink partner if exists
    if partner_id:
        await transactions_collection.update_one(
            {"_id": ObjectId(partner_id)},
            {"$set": {"is_transfer": False, "linked_tx_id": None}}
        )
        
    return {"message": "Transactions unlinked successfully"}

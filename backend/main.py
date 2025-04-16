from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from src.config import PINECONE_INDEX, EMBEDDER
from src.state import AgentState
from src.workflow import build_workflow
from pydantic import BaseModel, validator
import json
import logging
from dotenv import load_dotenv
import re

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

graph = build_workflow()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    user_id: str
    query: str

class UserDetails(BaseModel):
    age: float
    gender: str
    height: str
    weight: float
    preferences: str
    restrictions: str
    goal: str

    @validator('age')
    def validate_age(cls, age):
        if age <= 0:
            raise ValueError('Age must be a positive number')
        return age

    @validator('gender')
    def validate_gender(cls, gender):
        gender = gender.lower()
        if gender not in ['male', 'female', 'other']:
            raise ValueError('Gender must be male, female, or other')
        return gender

    @validator('height')
    def validate_height(cls, height):
        if not re.match(r"^\d+(\.\d+)?(cm|in)?$", height):
            raise ValueError("Invalid height format. Use digits with optional 'cm' or 'in'.")
        return height

    @validator('weight')
    def validate_weight(cls, weight):
        if weight <= 0:
            raise ValueError('Weight must be a positive number')
        return weight

def get_user_context_from_pinecone(user_id: str) -> dict:
    """Fetch user profile directly by fixed vector_id."""
    try:
        response = PINECONE_INDEX.fetch(ids=[f"{user_id}_profile"])
        logger.debug(f"Pinecone fetch for {user_id}: {response}")
        vectors = response.vectors
        if vectors and f"{user_id}_profile" in vectors:
            return vectors[f"{user_id}_profile"].metadata
        logger.warning(f"No profile found for user_id: {user_id}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching user context from Pinecone: {str(e)}")
        return {}

def store_user_details(user_id: str, details: UserDetails):
    """Store user profile in Pinecone with fixed vector_id."""
    try:
        details_dict = details.dict()

        profile_text = json.dumps(details_dict)
        embedding = EMBEDDER.embed_query(profile_text)
        vector_id = f"{user_id}_profile"
        metadata = {
            "user_id": user_id,
            "type": "user_profile",
            **details_dict
        }
        PINECONE_INDEX.upsert(vectors=[(vector_id, embedding, metadata)])
        logger.info(f"Stored profile for user_id: {user_id}")

        # Verify storage
        verify_response = PINECONE_INDEX.fetch(ids=[vector_id])
        logger.debug(f"Verification fetch for {user_id}: {verify_response}")
        if not verify_response.vectors or vector_id not in verify_response.vectors:
            logger.error(f"Failed to verify storage for {user_id}")
        else:
            logger.info(f"Verified profile storage for {user_id}: {verify_response.vectors[vector_id].metadata}")

        return {"message": f"Stored details for {user_id}", "user_id": user_id}
    except Exception as e:
        logger.error(f"Error storing user details for user_id: {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error storing user details")

@app.post("/submit-details/")
async def submit_details(
    user_id: str = Form(...),
    age: str = Form(...),
    gender: str = Form(...),
    height: str = Form(...),
    weight: str = Form(...),
    preferences: str = Form(...),
    restrictions: str = Form(...),
    goal: str = Form(...)
):
    try:
        details = UserDetails(
            age=float(age),
            gender=gender,
            height=height,
            weight=float(weight),
            preferences=preferences,
            restrictions=restrictions,
            goal=goal
        )
        result = store_user_details(user_id, details)
        return {"status": "success", "user_id": user_id}
    except Exception as e:
        logger.error(f"Error in submit-details for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))  # Return the error message

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        # Fetch user context from Pinecone
        user_context = get_user_context_from_pinecone(request.user_id)

        # Log the user context to check if `age` is available
        logger.debug(f"User context for {request.user_id}: {user_context}")

        if not user_context:
            return {"response": "No profile found. Please submit your details first."}

        initial_state = AgentState(
            user_id=request.user_id,
            user_query=request.query,
            user_context=user_context,  # Pre-populate with fetched data
            conversation_history=[],
            tool_calls=[],
            tool_outputs=[],
            response=""
        )

        # Log the state before invoking workflow
        logger.debug(f"Initial state before invoking workflow: {initial_state}")

        result = graph.invoke(initial_state)

        return {"response": result["response"]}
    except Exception as e:
        logger.error(f"Error in chat for user_id {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

from src.state import AgentState
from src.config import PINECONE_INDEX
import logging

logger = logging.getLogger(__name__)

def context_retrieval_node(state: AgentState) -> AgentState:
    user_id = state["user_id"]
    logger.debug(f"Attempting to fetch profile for user_id: {user_id}")
    
    try:
        response = PINECONE_INDEX.fetch(ids=[f"{user_id}_profile"])
        logger.debug(f"Pinecone fetch result for {user_id}: {response}")
        vectors = response.vectors
        if vectors and f"{user_id}_profile" in vectors:
            state["user_context"] = vectors[f"{user_id}_profile"].metadata
            #print(state["user_context"])
            logger.info(f"Successfully retrieved profile for {user_id}: {state['user_context']}")
        else:
            logger.warning(f"No profile found for user_id: {user_id} in vectors: {vectors}")
            print(f"No profile found for user_id: {user_id}")
            state["user_context"] = {}
            
    except Exception as e:
        logger.error(f"Error fetching Pinecone profile for {user_id}: {str(e)}")
        state["user_context"] = {}
    
    logger.debug(f"Updated user_context: {state['user_context']}")
    return state
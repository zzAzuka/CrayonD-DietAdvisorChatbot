from src.state import AgentState
from src.config import PINECONE_INDEX, EMBEDDER
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def pinecone_storage_node(state: AgentState) -> AgentState:
    user_id = state["user_id"]
    tool_outputs = state["tool_outputs"]
    
    if tool_outputs:
        try:
            for output in tool_outputs:
                tool_name = output["tool"]
                result = output["result"]
                timestamp = int(datetime.now().timestamp())
                vector_id = f"{user_id}_{tool_name}_{timestamp}"
                
                result_text = json.dumps(result) if isinstance(result, dict) else str(result)
                embedding = EMBEDDER.embed_query(result_text)
                
                metadata = {
                    "user_id": user_id,
                    "type": f"{tool_name}_result",
                    "timestamp": timestamp,
                    "result": result_text
                }
                
                PINECONE_INDEX.upsert(vectors=[(vector_id, embedding, metadata)])
                logger.debug(f"Stored {tool_name} result for user {user_id}: {vector_id}")
                
        except Exception as e:
            logger.error(f"Error storing tool outputs for {user_id}: {str(e)}")
    
    return state
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    user_query: str
    conversation_history: List[Dict[str, str]]
    user_context: Dict[str, Any]
    tool_outputs: List[Dict[str, Any]]
    response: str
    user_id: str
    tool_calls: List[Dict[str, Any]]
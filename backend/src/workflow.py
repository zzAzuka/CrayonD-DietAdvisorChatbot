import sys
import os
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.context_retrieval import context_retrieval_node
from src.nodes.llm import llm_node
from src.nodes.tool_router import tool_router_node
from src.nodes.pinecone_storage import pinecone_storage_node
from src.nodes.response_formatter import response_formatter_node

def route_after_llm(state: AgentState) -> str:
    if state.get("tool_calls"):
        return "tool_router"
    return "response_formatter" 

def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("context_retrieval", context_retrieval_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tool_router", tool_router_node)
    workflow.add_node("pinecone_storage", pinecone_storage_node)
    workflow.add_node("response_formatter", response_formatter_node)

    workflow.set_entry_point("context_retrieval")
    workflow.add_edge("context_retrieval", "llm")
    
    workflow.add_conditional_edges("llm", route_after_llm, {
        "tool_router": "tool_router",
        "response_formatter": "response_formatter"
    })

    workflow.add_edge("tool_router", "pinecone_storage")
    workflow.add_edge("pinecone_storage", "response_formatter")
    workflow.add_edge("response_formatter", END)
    workflow.set_entry_point("context_retrieval")

    return workflow.compile()
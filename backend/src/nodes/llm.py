import json
from src.state import AgentState
from src.config import LLM
from langchain_core.prompts import ChatPromptTemplate
from src.tools import TOOLS
import logging

logger = logging.getLogger(__name__)

def llm_node(state: AgentState) -> AgentState:
    llm_with_tools = LLM.bind_tools(TOOLS)
    
    user_context = state["user_context"].copy()
    required_fields = ["age", "gender", "height", "weight", "preferences", "restrictions", "goal"]
    for field in required_fields:
        if field not in user_context:
            user_context[field] = ""
    
    context_missing = all(user_context[field] == "" for field in required_fields)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a diet assistant with access to user context.
            User profile: Age: {age}, Gender: {gender}, Height: {height}, Weight: {weight}, Preferences: {preferences}, Restrictions: {restrictions}, Goal: {goal}.
            Based on the query, select the appropriate action:
            - For meal plans or diet advice (e.g., "meal plan", "diet for weight loss"), call 'diet_recommendations' with arguments: {{"age": {age}, "gender": "{gender}", "height": "{height}", "weight": {weight}, "preferences": "{preferences}", "restrictions": "{restrictions}", "goal": "{goal}"}}.
            - For recipe requests (e.g., "recipe for lasagna"), call 'recipe_fetcher' with the dish name and include preferences: "{preferences}", restrictions: "{restrictions}".
            - For nutritional info (e.g., "calories in pizza"), call 'nut_content_fetcher' with the dish name.
            - If any context field is empty for 'diet_recommendations', respond: "Please provide your age, gender, height, weight, preferences, restrictions, and goal."
            - For general questions, respond conversationally without tools.
            Do NOT bundle the context into a single 'input_data' string; use individual key-value pairs as arguments.
        """),
        *[(msg["role"], msg["content"]) for msg in state["conversation_history"]],
        ("user", "{user_query}")
    ])
    print("I am being executed blud")
    formatted_prompt = prompt.format_messages(
    age=str(state["user_context"]["age"]),  # Convert float to string
    gender=state["user_context"]["gender"],
    height=state["user_context"]["height"],
    weight=str(state["user_context"]["weight"]),
    preferences=state["user_context"]["preferences"],
    restrictions=state["user_context"]["restrictions"],
    goal=state["user_context"]["goal"],
    user_query=state["user_query"]
)
    response = llm_with_tools.invoke(formatted_prompt)
    logger.debug(f"LLM response: {response}")
    
    state["tool_calls"] = []  # Initialize tool_calls to an empty list

    if response.tool_calls:
        state["tool_outputs"] = []
        for call in response.tool_calls:
            logger.debug(f"Tool call: {call}")
            if call["name"] == "diet_recommendations" and context_missing:
                state["response"] = "Please provide your age, gender, height, weight, preferences, restrictions, and goal."
                break
            
            tool_args = call["args"].copy()  # Create a copy of call["args"]
            
            if call["name"] == "recipe_fetcher":
                tool_args["preferences"] = user_context.get("preferences", "")
                tool_args["restrictions"] = user_context.get("restrictions", "")
            
            state["tool_outputs"].append({"tool": call["name"], "args": tool_args})
            state["tool_calls"].append({"name": call["name"], "args": tool_args}) # Append to tool_calls
        
        if not state["tool_outputs"] and not state.get("response"):  # Check if tool_outputs is empty after processing
            state["response"] = "I don't have enough information to answer."
            
    else:
        state["response"] = response.content or "I don't have enough information to answer."
    
    state["conversation_history"].append({"role": "user", "content": state["user_query"]})
    if state.get("response"):
        state["conversation_history"].append({"role": "assistant", "content": state["response"]})
    
    return state

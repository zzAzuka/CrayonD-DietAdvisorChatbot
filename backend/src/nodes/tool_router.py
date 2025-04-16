from src.state import AgentState
from src.tools import TOOLS
import traceback
import logging

logger = logging.getLogger(__name__)

def tool_router_node(state: AgentState) -> AgentState:
    
    logger.debug(f"Running tool_router with tool_calls: {state['tool_calls']}")
    print(f"Running tool_router with tool_calls: {state['tool_calls']}")
    tool_outputs = []
    
    tool_map = {tool.name: tool for tool in TOOLS}
    
    for call in state["tool_calls"]:
        tool_name = call["name"]
        args = call["args"]
        #print(args)
        logger.debug(f"Executing tool: {tool_name} with args: {args}")
        
        try:
            tool = tool_map.get(tool_name)
            if not tool:
                tool_outputs.append({
                    "tool": tool_name,
                    "result": f"Error: Tool '{tool_name}' not found."
                })
                continue
            
            result = tool.invoke(args)
            #print(f"Tool {tool_name} raw result: {result}")
            logger.debug(f"Tool {tool_name} raw result: {result}")
            
            if tool_name == "diet_recommendations" and isinstance(result, dict):
                tool_outputs.append({
                    "tool": tool_name,
                    "result": result
                })
            elif tool_name == "recipe_fetcher":
                tool_outputs.append({
                    "tool": tool_name,
                    "result": result["result"] if isinstance(result, dict) and "result" in result else "Error: Content not found"
                })
            else:
                result_str = str(result) if not isinstance(result, str) else result
                tool_outputs.append({
                    "tool": tool_name,
                    "result": result_str
                })
                
        except Exception as e:
            error_message = traceback.format_exc()
            tool_outputs.append({
                "tool": tool_name,
                "result": f"Error executing tool: {str(e)}. Details: {error_message}"
            })
            logger.error(f"Tool error: {str(e)}, Traceback: {error_message}")
    
    state["tool_outputs"] = tool_outputs  # Update state with the new tool_outputs
    logger.debug(f"Tool outputs: {state['tool_outputs']}")
    return state

from src.state import AgentState

def response_formatter_node(state: AgentState) -> AgentState:
    print(f"DEBUG: Entering response_formatter with tool_outputs: {state['tool_outputs']}")
    
    if state.get("response"):
        print(f"DEBUG: Response already set: {state['response']}")
        return state
    
    if state["tool_outputs"]:
        response_parts = []
        for output in state["tool_outputs"]:
            print("OUTPUT:", output)
            tool_name = output["tool"]
            result = output["result"]
            print(f"DEBUG: Processing output for tool: {tool_name}, result: {result}")
            
            if tool_name == "diet_recommendations":
                if isinstance(result, dict) and "daily_calories" in result and "meal_plan" in result:
                    meal_plan = result["meal_plan"].strip()
                    if meal_plan and not meal_plan.lower().startswith(("error", "unable")):
                        response_parts.append(
                            f"### Meal Plan\n\n"
                            f"Recommended daily calories: {result['daily_calories']}\n\n"
                            f"{meal_plan}"
                        )
                    else:
                        print(f"DEBUG: Invalid meal plan content: {meal_plan}")
                        response_parts.append(
                            f"### Meal Plan\n\n"
                            f"Recommended daily calories: N/A\n\n"
                            f"Unable to generate a valid meal plan."
                        )
                else:
                    print(f"DEBUG: Invalid diet tool result format: {result}")
                    response_parts.append(
                        f"### Meal Plan\n\n"
                        f"Recommended daily calories: N/A\n\n"
                        f"No valid plan found."
                    )
            elif tool_name == "recipe_fetcher":
                if isinstance(result, dict) and "content" in result:
                    content = result["content"].strip()
                    if result.get("awaiting_confirmation", False):
                        response_parts.append(
                            f"### Recipe Confirmation\n\n"
                            f"{content}"
                        )
                    elif result.get("status") == "error":
                        response_parts.append(
                            f"### Recipe\n\n"
                            f"Error: {content}"
                        )
                    else:
                        response_parts.append(
                            f"### Recipe\n\n"
                            f"{content}"
                        )
                else:
                    print(f"DEBUG: Invalid recipe result format: {result}")
                    response_parts.append(
                        f"### Recipe\n\n"
                        f"Error: No valid recipe found."
                    )
            elif tool_name == "nut_content_fetcher":
                response_parts.append(
                    #f"### Nutritional Content\n\n"
                    f"{str(result)}"
                )
    
        state["response"] = "\n\n".join(response_parts)
    else:
        print("DEBUG: No tool outputs received")
        state["response"] = "I don't have enough information to answer. Can you clarify?"
    
    state["conversation_history"].append({"role": "assistant", "content": state["response"]})
    print(f"DEBUG: Final response: {state['response']}")
    return state
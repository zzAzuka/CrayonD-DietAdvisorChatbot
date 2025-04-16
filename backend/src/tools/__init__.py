from langchain_core.tools import StructuredTool
from src.config import LLM
import requests
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
import json
import re

class DietRecommendationsInput(BaseModel):
    age: str  # Accepts "60.0"; will convert to float/int
    gender: str
    height: str
    weight: str
    preferences: str
    restrictions: str
    goal: str

def diet_recommendations(
    age: str,
    gender: str,
    height: str,
    weight: str,
    preferences: str,
    restrictions: str,
    goal: str
) -> dict:
    
    """Generates a personalized meal plan based on user details."""
    input_data = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "preferences": preferences,
        "restrictions": restrictions,
        "goal": goal
    }
    print(input_data)
    try:
        age = int(float(input_data["age"]))
        if age <= 0:
            age = 30
    except (TypeError, ValueError):
        age = 30
    
    gender = input_data["gender"].lower().strip()
    if gender not in ["male", "female"]:
        gender = "male"
    
    # Process height with better validation
    height = input_data["height"].strip()
    try:
        if "'" in height:
            feet, inches = height.split("'")
            inches = inches.strip('"')
            height_inches = int(feet) * 12 + float(inches)
        elif "cm" in height.lower():
            height_cm = float(height.lower().replace("cm", "").strip())
            height_inches = height_cm / 2.54
        else:
            height_inches = float(height)
        if height_inches <= 0:
            height_inches = 67  # More average default (5'7")
    except (ValueError, TypeError):
        height_inches = 67
    height_cm = height_inches * 2.54
    
    # Process weight with better validation
    try:
        weight = float(input_data["weight"])
        if weight <= 0:
            weight = 154  # More average default
    except (TypeError, ValueError):
        weight = 154

    weight_kg = weight 
    
    preferences = input_data["preferences"].strip() or "none"
    restrictions = input_data["restrictions"].strip() or "none"
    goal = input_data["goal"].lower().strip() or "maintenance"
    if goal not in ["weight_loss", "muscle_gain", "maintenance"]:
        goal = "maintenance"
    
    # BMR calculation
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Calorie adjustment
    if goal == "weight_loss":
        calories = bmr * 1.2 - 500
    elif goal == "muscle_gain":
        calories = bmr * 1.6 + 300 
    else:
        calories = bmr * 1.4
    calories = max(calories, 1800)
    
    is_vegetarian = "vegetarian" in preferences.lower() or "veg" in preferences.lower()
    no_dairy = "no dairy" in restrictions.lower() or "dairy-free" in restrictions.lower()
    is_non_veg = "non-veg" in preferences.lower() or "meat" in preferences.lower() or "non-vegetarian" in preferences.lower()
    
    # Build comprehensive prompt with all constraints upfront to avoid regeneration
    prompt = f"""
    Create a daily meal plan for a user with these exact requirements:
    - Age: {age}
    - Gender: {gender}
    - Height: {height_cm}cm
    - Weight: {weight_kg}kg
    - Preferences: {preferences}
    - Restrictions: {restrictions}
    - Goal: {goal}
    - Target calories: {round(calories)}
    
    Requirements (you MUST follow ALL these guidelines):
    - Generate exactly 4 meals (breakfast, lunch, dinner, snack)
    - Each meal should have a calorie estimate, with total ~{round(calories)} calories
    - Brief descriptions (1-2 sentences per meal)
    - Format as a numbered list (1. Meal: description (~calories calories))
    {f'- This is a VEGETARIAN plan: NO meat, fish, poultry, or animal products allowed' if is_vegetarian else ''}
    {f'- This is a NON-VEGETARIAN plan: MUST include at least one meal with chicken, beef, fish, or poultry' if is_non_veg else ''}
    {f'- NO DAIRY allowed: No milk, cheese, yogurt, or butter (use plant-based alternatives instead)' if no_dairy else ''}
    {f'- For muscle gain goal: Include high-protein foods in each meal' if goal == "muscle_gain" else ''}
    
    Review your meal plan carefully before finalizing to ensure it follows ALL requirements precisely.
    Return only the meal plan text with no explanations or comments.
    """
    
    print(prompt)
    try:
        response = LLM.invoke(prompt)
        meal_plan = response.content.strip() or "Unable to generate compliant meal plan."
        
        # Validate the result against critical requirements
        validation_failed = False
        error_reason = ""
        
        if no_dairy and any(x in meal_plan.lower() for x in ["yogurt", "cheese", "milk", "butter"]):
            validation_failed = True
            error_reason = "dairy restriction violation"
        
        if is_vegetarian and any(x in meal_plan.lower() for x in ["chicken", "salmon", "beef", "fish", "poultry", "meat"]):
            validation_failed = True
            error_reason = "vegetarian restriction violation"
        
        if is_non_veg and not any(x in meal_plan.lower() for x in ["chicken", "salmon", "beef", "fish", "poultry", "meat"]):
            validation_failed = True
            error_reason = "non-vegetarian requirement not met"
        
        # If validation failed, make one more attempt with a stronger prompt
        if validation_failed:
            correction_prompt = f"""
            The previous meal plan failed validation due to: {error_reason}.
            
            Create a NEW daily meal plan that strictly follows these requirements:
            - Target calories: {round(calories)}
            {f'- VEGETARIAN ONLY: NO meat, fish, poultry, or animal products' if is_vegetarian else ''}
            {f'- NON-VEGETARIAN: MUST include at least one meal with chicken, beef, fish, or poultry' if is_non_veg else ''}
            {f'- NO DAIRY ALLOWED: No milk, cheese, yogurt, or butter' if no_dairy else ''}
            
            Generate 4 meals (breakfast, lunch, dinner, snack) with calories totaling ~{round(calories)}.
            Format as numbered list. Focus only on meeting the dietary requirements.
            """
            
            response = LLM.invoke(correction_prompt)
            meal_plan = response.content.strip() or "Unable to generate compliant meal plan."
            
            # Final validation check
            if (no_dairy and any(x in meal_plan.lower() for x in ["yogurt", "cheese", "milk", "butter"])) or \
               (is_vegetarian and any(x in meal_plan.lower() for x in ["chicken", "salmon", "beef", "fish", "poultry", "meat"])) or \
               (is_non_veg and not any(x in meal_plan.lower() for x in ["chicken", "salmon", "beef", "fish", "poultry", "meat"])):
                meal_plan = "Unable to generate a meal plan that meets all your dietary requirements. Please consider adjusting your restrictions or preferences."

    except Exception as e:
        meal_plan = f"Unable to generate meal plan: {str(e)}"

    return {
        "daily_calories": round(calories),
        "meal_plan": meal_plan
    }

diet_recommendations_tool = StructuredTool.from_function(
    func=diet_recommendations,
    name="diet_recommendations",
    description="Generates a personalized meal plan based on age, gender, height, weight, preferences, restrictions, and goal.",
    args_schema=DietRecommendationsInput
)

def recipe_fetcher(recipe_name: str, preferences: str = "", restrictions: str = "") -> dict:
    """
    Fetches a recipe from TheMealDB API or generates one via LLM if no match.
    Validates preferences/restrictions and prompts if mismatched.
    """
    print(f"DEBUG: Running recipe_fetcher with recipe_name='{recipe_name}', "
          f"preferences='{preferences}', restrictions='{restrictions}'")
    
    recipe_name = recipe_name.strip().lower() if recipe_name else ""
    preferences = preferences.strip().lower() if preferences else ""
    restrictions = restrictions.strip().lower() if restrictions else ""
    
    if not recipe_name:
        return {
            "tool": "recipe_fetcher",
            "result": {"content": "Error: Recipe name is required.", "status": "error"}
        }
    
    # TheMealDB API
    base_url = "https://www.themealdb.com/api/json/v1/1"
    url = f"{base_url}/search.php?s={requests.utils.quote(recipe_name)}"
    print(f"DEBUG: Sending request to {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        meals = data.get("meals")
        
        if not meals:
            print(f"DEBUG: No recipes found for '{recipe_name}'")
        else:
            meal = meals[0]
            ingredients = [
                meal.get(f"strIngredient{i}", "").lower()
                for i in range(1, 21)
                if meal.get(f"strIngredient{i}")
            ]
            meal_name = meal.get("strMeal", "").lower()
            category = meal.get("strCategory", "").lower()
            tags = meal.get("strTags", "").lower()
            
            ingredients_list = [
                f"- {meal.get(f'strMeasure{i}', '')} {meal.get(f'strIngredient{i}', '')}".strip()
                for i in range(1, 21)
                if meal.get(f"strIngredient{i}") and meal.get(f"strIngredient{i}").strip()
            ]
            
            validation_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                    You are a diet assistant. Determine if a recipe matches user preferences and restrictions with high accuracy.
                    Recipe: {recipe_name}
                    Category: {category}
                    Tags: {tags}
                    Ingredients: {ingredients}
                    User Preferences: {preferences}
                    User Restrictions: {restrictions}
                    
                    - Preferences (e.g., non-vegetarian) mean the recipe MUST include meat or animal products unless specified otherwise.
                    - Restrictions (e.g., no dairy) mean those ingredients MUST be absent.
                    - Return true for 'matches' only if the recipe fully aligns with preferences and has no restricted ingredients.
                    
                    Respond with a JSON object only:
                    {{"matches": true/false, "reason": "Detailed explanation if it doesn't match"}}
                """),
                ("user", "Validate the recipe.")
            ])
            
            try:
                validation_response = LLM.invoke(validation_prompt.format_messages(
                    recipe_name=meal_name,
                    category=category,
                    tags=tags,
                    ingredients=", ".join(ingredients),
                    preferences=preferences or "none",
                    restrictions=restrictions or "none"
                ))
                
                try:
                    validation_text = validation_response.content
                    validation_text = re.search(r'\{.*\}', validation_text, re.DOTALL)
                    if validation_text:
                        validation = json.loads(validation_text.group(0))
                    else:
                        matches = "true" in validation_response.content.lower() and "matches: true" in validation_response.content.lower()
                        reason = re.search(r'reason:?\s*(.*?)(?:\n|$)', validation_response.content, re.DOTALL)
                        reason = reason.group(1) if reason else "Unknown validation issue"
                        validation = {"matches": matches, "reason": reason}
                except Exception as e:
                    print(f"DEBUG: Validation parsing error: {str(e)}")
                    validation = {"matches": False, "reason": "Could not validate recipe against preferences"}
                
                print(f"DEBUG: LLM validation: {validation}")
                
                if validation.get("matches", False):
                    result = (
                        f"Recipe for {meal['strMeal']}\n\n"
                        f"Ingredients:\n\n" + "\n\n".join(ingredients_list) + "\n\n"
                        f"Instructions:\n\n{meal.get('strInstructions', 'No instructions provided.')}\n\n"
                        f"Source: {meal.get('strSource', 'TheMealDB')}"
                    )
                    return {
                        "tool": "recipe_fetcher",
                        "result": {"content": result, "status": "success"}
                    }
                else:
                    return {
                        "tool": "recipe_fetcher",
                        "result": {
                            "content": (
                                f"The recipe '{meal_name}' doesn't match your preferences ('{preferences}') "
                                f"or restrictions ('{restrictions}'). Reason: {validation.get('reason', 'Not specified')}\n"
                                "Do you still want this recipe? (Please respond 'yes' or 'no'.)"
                            ),
                            "status": "pending",
                            "awaiting_confirmation": True,
                            "recipe_data": {
                                "name": meal["strMeal"],
                                "ingredients": ingredients_list,
                                "instructions": meal.get("strInstructions", ""),
                                "source": meal.get("strSource", "TheMealDB")
                            }
                        }
                    }
            except Exception as e:
                print(f"DEBUG: LLM validation error: {str(e)}")
        
        # Fallback to LLM generation
        fallback_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a diet assistant. Generate a recipe respecting user preferences and restrictions.
                Guidelines:
                - If preferences mention 'vegetarian', use NO meat, fish, or poultry.
                - If restrictions mention 'no dairy', use NO milk, cheese, butter, or yogurt.
                - If preferences mention 'non-veg', include meat, fish, or poultry.
            """),
            ("user", f"""
                Generate a recipe for {recipe_name}.
                Preferences: {preferences}
                Restrictions: {restrictions}
                
                Format as a numbered list:
                1. Ingredients
                2. Instructions
                
                Recipe for {recipe_name}
                1. Ingredients:
                   - ingredient 1
                   - ingredient 2
                2. Instructions:
                   1. Step 1
                   2. Step 2
            """)
        ])
        
        try:
            fallback_response = LLM.invoke(fallback_prompt.format_messages())
            result = fallback_response.content.strip()
            print(f"DEBUG: Fallback recipe generated: {result}")
            return {
                "tool": "recipe_fetcher",
                "result": {"content": result, "status": "success"}
            }
        except Exception as e:
            print(f"DEBUG: Fallback recipe error: {str(e)}")
            return {
                "tool": "recipe_fetcher",
                "result": {"content": f"Error generating recipe: {str(e)}", "status": "error"}
            }
            
    except requests.RequestException as e:
        print(f"DEBUG: TheMealDB API error: {str(e)}")
        return {
            "tool": "recipe_fetcher",
            "result": {"content": f"Error fetching recipe: {str(e)}", "status": "error"}
        }

recipe_fetcher_tool = StructuredTool.from_function(
    func=recipe_fetcher,
    name="recipe_fetcher",
    description="Fetches a recipe for a requested dish using TheMealDB API, respecting user preferences and restrictions."
)

def nut_content_fetcher(dish_name: str) -> str:
    """Fetches nutritional information for a dish using DuckDuckGo search."""

    dish_name = dish_name.strip() if dish_name else ""
    if not dish_name:
        return "Error: Dish name is required."
    
    search = DuckDuckGoSearchRun()
    query = f"nutritional content of {dish_name} calories protein fat carbs macro-nutrients and micro-nutrients"
    try:
        result = search.invoke(query)
        good_prompt=f"""
            Instructions

            This is the context collected from the internet regarding the nutritional content of {dish_name}.
            Context: {result}

            Task

            Using the provided context, extract and format the following nutritional information for {dish_name}:

            Macronutrients: Calories, Carbohydrates, Fats, Proteins
            Micronutrients: Vitamins and Minerals

            Guidelines
            Focus solely on the nutritional content relevant to {dish_name}.

            Present the information in a structured format with each component as a subheading, followed by its specifications.

            If specific values (e.g., for vitamins or minerals) are unavailable in the context, note the absence and suggest a reliable source (e.g., USDA FoodData Central database) for further details.
                    """
                
        good_response = LLM.invoke(good_prompt)
        return f"### Nutritional Content of {dish_name}\n\n{good_response.content}"
    except Exception as e:
        return f"Error fetching nutritional data: {str(e)}"

nut_content_fetcher_tool = StructuredTool.from_function(
    func=nut_content_fetcher,
    name="nut_content_fetcher",
    description="Fetches nutritional information (calories, protein, fat, carbs) for a dish using DuckDuckGo."
)

TOOLS = [diet_recommendations_tool, recipe_fetcher_tool, nut_content_fetcher_tool]
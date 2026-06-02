import json

def estimate_recipe_details(recipe):
    category = recipe.get("category", "MAIN DISHES").upper()
    instructions = recipe.get("instructions", [])
    num_steps = len(instructions)
    
    # Defaults
    prep_time = 10
    cook_time = 15
    servings = 2
    difficulty = "Easy"
    
    if "BEVERAGES" in category or "DRINKS" in category:
        prep_time = 5 if num_steps <= 1 else 10
        cook_time = 0
        servings = 2
        difficulty = "Easy"
        
    elif "SOUPS" in category or "BROTHS" in category:
        prep_time = 10
        cook_time = 15 if num_steps <= 2 else 20
        servings = 4
        difficulty = "Easy" if num_steps <= 2 else "Medium"
        
    elif "SALADS" in category or "DRESSINGS" in category:
        prep_time = 10 if num_steps <= 2 else 15
        cook_time = 0 if "grill" not in str(instructions).lower() and "roast" not in str(instructions).lower() else 10
        servings = 2 if num_steps <= 2 else 4
        difficulty = "Easy"
        
    elif "MAIN DISHES" in category or "DALS & LENTILS" in category:
        prep_time = 15 if num_steps <= 3 else 20
        cook_time = 20 if num_steps <= 3 else 30
        servings = 4
        difficulty = "Medium" if num_steps >= 3 else "Easy"
        
    elif "RICE" in category or "GRAINS" in category:
        prep_time = 10
        cook_time = 15 if num_steps <= 2 else 25
        servings = 4
        difficulty = "Easy" if num_steps <= 2 else "Medium"
        
    elif "SIDES" in category or "CHUTNEYS" in category:
        prep_time = 10
        cook_time = 5 if "cook" not in str(instructions).lower() and "sauté" not in str(instructions).lower() else 10
        servings = 4
        difficulty = "Easy"
        
    elif "DESSERTS" in category or "SWEETS" in category:
        prep_time = 15
        cook_time = 0 if "bake" not in str(instructions).lower() and "cook" not in str(instructions).lower() else 15
        servings = 4
        difficulty = "Medium" if num_steps >= 4 else "Easy"
        
    elif "BREAKFAST" in category:
        prep_time = 10
        cook_time = 10 if num_steps <= 2 else 15
        servings = 2
        difficulty = "Easy" if num_steps <= 2 else "Medium"

    # Refine based on steps content
    instructions_text = " ".join(instructions).lower()
    if "soaking" in instructions_text or "soak" in instructions_text:
        prep_time += 10 # add soaking time indicator (e.g. 10 mins active prep)
    if "bake" in instructions_text or "roast" in instructions_text:
        cook_time = max(cook_time, 25)
    if "boil" in instructions_text and cook_time == 0:
        cook_time = 10

    recipe["prepTime"] = prep_time
    recipe["cookTime"] = cook_time
    recipe["totalTime"] = prep_time + cook_time
    recipe["servings"] = servings
    recipe["difficulty"] = difficulty

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
        
    for recipe in recipes:
        estimate_recipe_details(recipe)
        
    with open('data/recipes.json', 'w') as f:
        json.dump(recipes, f, indent=2)
        
    print(f"Successfully added prep/cook/total times, servings, and difficulty to {len(recipes)} recipes!")

if __name__ == '__main__':
    main()

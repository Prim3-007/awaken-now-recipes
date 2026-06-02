import json
import re

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)

    # Patterns for prohibited items and their byproducts
    prohibited_patterns = {
        "onion": r'\b(onion(?:s|\s+powder|\s+paste|\s+flakes)?|pyaaj|pyaz|kanda)\b',
        "garlic": r'\b(garlic(?:\s+powder|\s+paste|\s+flakes)?|lahsun|lasun)\b',
        "tomato": r'\b(tomato(?:es|\s+paste|\s+puree|\s+sauce|\s+ketchup)?|tamatar)\b',
        "mushroom": r'\b(mushroom(?:s|\s+powder)?|guchhi|khumb)\b',
        "refined sugar": r'\b(refined sugar|white sugar|cane sugar|icing sugar|(?<!coconut\s)(?<!date\s)(?<!maple\s)(?<!palm\s)\bsugar\b)\b',
        "eggplant": r'\b(eggplant(?:s)?|brinjal(?:s)?|aubergine(?:s)?|baingan)\b',
        "ginger powder": r'\b(dry ginger powder|ginger powder|ginger\s*\(powder|dry ginger|sonth)\b'
    }

    print("=== PROHIBITED BYPRODUCTS AUDIT ===")
    found_violations = {}

    for recipe in recipes:
        recipe_violations = []
        # Check ingredients
        for ing in recipe["ingredients"]:
            for name, pattern in prohibited_patterns.items():
                if re.search(pattern, ing, re.IGNORECASE):
                    # For refined sugar, make sure it's not a false positive
                    # For onion, make sure it's not 'spring onion greens'
                    if name == "onion" and "spring onion" in ing.lower():
                        continue # spring onion greens are allowed
                    recipe_violations.append((f"Ingredient: '{ing}'", name))
        
        # Check instructions
        for idx, step in enumerate(recipe["instructions"]):
            for name, pattern in prohibited_patterns.items():
                if re.search(pattern, step, re.IGNORECASE):
                    if name == "onion" and "spring onion" in step.lower():
                        continue
                    recipe_violations.append((f"Instruction Step {idx+1}: '{step}'", name))

        if recipe_violations:
            found_violations[recipe["id"]] = {
                "name": recipe["name"],
                "violations": recipe_violations
            }

    print(f"Total recipes with violations: {len(found_violations)}")
    for rid, info in found_violations.items():
        print(f"\n* Recipe: '{info['name']}' (ID: {rid})")
        for loc, term in info["violations"]:
            print(f"  - [{term.upper()}] Found in {loc}")

if __name__ == '__main__':
    main()

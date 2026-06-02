import json
import re

def audit_and_substitute():
    # 1. Load existing recipes
    try:
        with open('data/recipes.json', 'r') as f:
            recipes = json.load(f)
    except FileNotFoundError:
        print("Error: recipes.json not found. Run parse_pdfs.py first.")
        return

    # 2. Inject a mock non-compliant recipe to demonstrate the substitution engine
    mock_recipe = {
        "id": "recipe_test_noncompliant",
        "name": "Baingan Tamatar Masala (Eggplant Tomato Curry)",
        "category": "MAIN DISHES",
        "ingredients": [
            "eggplant",
            "tomatoes",
            "onion",
            "garlic",
            "ghee",
            "turmeric",
            "salt",
            "refined sugar"
        ],
        "instructions": [
            "Chop the eggplant and tomatoes into cubes.",
            "Finely dice the onion and garlic.",
            "In a pan, heat ghee and sauté onion and garlic until soft.",
            "Add turmeric, eggplant, tomatoes, and salt.",
            "Stir in refined sugar and simmer until the eggplant is tender.",
            "Serve hot."
        ],
        "description": "A rich traditional eggplant and tomato curry made with onions and garlic.",
        "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&q=80&w=600"
    }
    
    # Check if the test recipe is already in the list; if not, append it
    if not any(r['id'] == 'recipe_test_noncompliant' for r in recipes):
        recipes.append(mock_recipe)
        print("Injected non-compliant test recipe 'Baingan Tamatar Masala'.")

    # 3. Define substitution mappings (regex -> replacement)
    # Using tuple of (pattern, replacement, display_name) for easy logging
    substitutions = [
        (r'\b(onion[s]?|pyaaj|pyaz|kanda)\b', 'spring onion greens (hara pyaaj)', 'onion'),
        (r'\b(tomato(?:es)?|tamatar)\b', 'raw papaya', 'tomato'),
        (r'\b(eggplant[s]?|brinjal[s]?|aubergine[s]?|baingan)\b', 'ash gourd', 'eggplant'),
        (r'\b(garlic|lahsun|lasun)\b', 'ginger', 'garlic'),
        (r'\b(mushroom[s]?|guchhi|khumb)\b', 'cauliflower', 'mushroom'),
        (r'\b(refined sugar|white sugar|cane sugar)\b', 'jaggery', 'refined sugar'),
        # Match 'sugar' if not preceded by allowed sweeteners
        (r'\b(?<!coconut\s)(?<!date\s)(?<!maple\s)(?<!palm\s)sugar\b', 'jaggery', 'refined sugar'),
        (r'\b(dry ginger powder|ginger powder|ginger\s*\(powder|dry ginger|sonth)\b', 'grated fresh ginger', 'ginger powder')
    ]

    updated_count = 0

    # 4. Iterate and audit
    for recipe in recipes:
        applied_subs = []
        
        # Audit ingredients
        new_ingredients = []
        for ing in recipe['ingredients']:
            updated_ing = ing
            for pattern, replacement, term_name in substitutions:
                if re.search(pattern, updated_ing, re.IGNORECASE):
                    updated_ing = re.sub(pattern, replacement, updated_ing, flags=re.IGNORECASE)
                    if term_name not in applied_subs:
                        applied_subs.append(term_name)
            new_ingredients.append(updated_ing)
            
        # Audit instructions
        new_instructions = []
        for step in recipe['instructions']:
            updated_step = step
            for pattern, replacement, term_name in substitutions:
                if re.search(pattern, updated_step, re.IGNORECASE):
                    updated_step = re.sub(pattern, replacement, updated_step, flags=re.IGNORECASE)
                    if term_name not in applied_subs:
                        applied_subs.append(term_name)
            new_instructions.append(updated_step)

        # Update recipe fields if substitutions occurred
        if applied_subs:
            recipe['ingredients'] = new_ingredients
            recipe['instructions'] = new_instructions
            recipe['substituted'] = True
            
            # Format nicely
            subs_str = ", ".join(f"replaced {term}" for term in applied_subs)
            recipe['substitutionNotes'] = f"Dietary adjustments applied: {subs_str}."
            
            # Update name if it contains eggplant or tomato
            old_name = recipe['name']
            for pattern, replacement, _ in substitutions:
                recipe['name'] = re.sub(pattern, replacement, recipe['name'], flags=re.IGNORECASE)
            
            # Title case the name for clean visual presentation
            recipe['name'] = recipe['name'].title()
            
            if old_name != recipe['name']:
                print(f"Renamed recipe: '{old_name}' -> '{recipe['name']}'")
            
            print(f"Audited and adjusted recipe '{recipe['name']}': {recipe['substitutionNotes']}")
            updated_count += 1
        else:
            recipe['substituted'] = False
            recipe['substitutionNotes'] = "Verified compliant with dietary guidelines."

    # 5. Write back to recipes.json
    with open('data/recipes.json', 'w') as f:
        json.dump(recipes, f, indent=2)

    print(f"\nAudit complete! Processed {len(recipes)} recipes. Applied substitutions to {updated_count} recipes.")

if __name__ == '__main__':
    audit_and_substitute()

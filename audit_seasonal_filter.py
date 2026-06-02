import json

def validate_recipe_for_season_js(recipe, season_key, seasons_data):
    # Emulate the frontend JS matching logic exactly
    season = seasons_data.get(season_key)
    if not season:
        return False, recipe["ingredients"]

    allowed_items = [
        item.lower().strip()
        for item in (season["allowedProduce"] + season["evergreenStaples"])
    ]

    unmatched_ingredients = []
    matched_details = []

    for ingredient in recipe["ingredients"]:
        ing_lower = ingredient.lower().strip()
        is_match = False
        matched_by = None

        for allowed in allowed_items:
            # Direct containment
            if ing_lower in allowed or allowed in ing_lower:
                is_match = True
                matched_by = allowed
                break
            
            # Simple plural removal match
            singular_ing = ing_lower[:-1] if ing_lower.endswith('s') else ing_lower
            singular_allowed = allowed[:-1] if allowed.endswith('s') else allowed
            if singular_ing in singular_allowed or singular_allowed in singular_ing:
                is_match = True
                matched_by = allowed
                break

        if not is_match:
            unmatched_ingredients.append(ingredient)
        else:
            matched_details.append((ingredient, matched_by))

    return len(unmatched_ingredients) == 0, unmatched_ingredients, matched_details

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
    with open('data/seasonal_produce.json', 'r') as f:
        produce_data = json.load(f)

    seasons = produce_data["seasons"]
    
    with open('seasonal_audit_full.txt', 'w') as out:
        out.write("=== SEASONAL AUDIT REPORT (JS EMULATION) ===\n")
        for season_key, season_info in seasons.items():
            out.write(f"\n==================================================\n")
            out.write(f"Season: {season_info['displayName']} ({season_key.upper()})\n")
            out.write(f"==================================================\n")
            matched_recipes = []
            for recipe in recipes:
                is_match, unmatched, matched_details = validate_recipe_for_season_js(recipe, season_key, seasons)
                if is_match:
                    matched_recipes.append((recipe, matched_details))

            out.write(f"Number of displaying recipes: {len(matched_recipes)}\n")
            
            if not matched_recipes:
                out.write("  No recipes matched.\n")
                continue

            for recipe, matched_details in matched_recipes:
                out.write(f"\n  * Recipe: '{recipe['name']}' (ID: {recipe['id']})\n")
                out.write("    Ingredients:\n")
                potential_issues = []
                for ing, matched_by in matched_details:
                    ing_clean = ing.lower().strip()
                    matched_clean = matched_by.lower().strip()
                    
                    is_weak = False
                    if ing_clean != matched_clean:
                        sing_ing = ing_clean[:-1] if ing_clean.endswith('s') else ing_clean
                        sing_matched = matched_clean[:-1] if matched_clean.endswith('s') else matched_clean
                        if sing_ing != sing_matched:
                            is_weak = True

                    status_str = "OK"
                    if is_weak:
                        status_str = "⚠️ WARNING (Partial Match)"
                        potential_issues.append((ing, matched_by))
                    
                    out.write(f"      - '{ing}' matched to allowed list item '{matched_by}' [{status_str}]\n")

                if potential_issues:
                    out.write("    ⚠️ POTENTIAL MISMATCHES (Out-of-season/disallowed ingredient matched via substring):\n")
                    for ing, matched_by in potential_issues:
                        out.write(f"      - Ingredient '{ing}' matched to '{matched_by}'\n")

if __name__ == '__main__':
    main()

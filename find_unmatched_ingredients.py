import json
import re

def clean_and_tokenize(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return [w for w in text.split() if w]

def singularize(word):
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word

def is_word_match(w1, w2):
    return singularize(w1) == singularize(w2)

def is_phrase_match(allowed_phrase, ing_phrase):
    allowed_words = clean_and_tokenize(allowed_phrase)
    ing_words = clean_and_tokenize(ing_phrase)
    
    if not allowed_words or not ing_words:
        return False
        
    for i in range(len(ing_words) - len(allowed_words) + 1):
        match = True
        for j in range(len(allowed_words)):
            if not is_word_match(allowed_words[j], ing_words[i+j]):
                match = False
                break
        if match:
            return True

    generic_words = {'leaves', 'water', 'powder', 'oil', 'salt', 'juice', 'seeds', 'pods', 'strands', 'greens', 'regular', 'dry', 'fresh', 'pinch', 'large', 'small'}
    
    for i in range(len(allowed_words) - len(ing_words) + 1):
        match = True
        for j in range(len(ing_words)):
            if not is_word_match(ing_words[j], allowed_words[i+j]):
                match = False
                break
        if match:
            has_non_generic = any(singularize(w) not in generic_words for w in ing_words)
            if has_non_generic:
                return True

    return False

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
    with open('data/seasonal_produce.json', 'r') as f:
        produce_data = json.load(f)

    seasons = produce_data["seasons"]
    
    all_unmatched_counts = {}
    recipe_unmatched = {}

    for recipe in recipes:
        # Check matching for each season
        seasons_matched = []
        unmatched_per_season = {}
        for season_key, season_info in seasons.items():
            allowed_items = season_info["allowedProduce"] + season_info["evergreenStaples"]
            unmatched = []
            for ingredient in recipe["ingredients"]:
                is_match = False
                for allowed in allowed_items:
                    if is_phrase_match(allowed, ingredient):
                        is_match = True
                        break
                if not is_match:
                    unmatched.append(ingredient)
            if not unmatched:
                seasons_matched.append(season_key)
            else:
                unmatched_per_season[season_key] = unmatched

        recipe_unmatched[recipe["id"]] = {
            "name": recipe["name"],
            "matched_seasons": seasons_matched,
            "unmatched_per_season": unmatched_per_season
        }

    # Count how many recipes match 0 seasons
    not_matched = [rid for rid, info in recipe_unmatched.items() if not info["matched_seasons"]]
    print(f"Total recipes: {len(recipes)}")
    print(f"Recipes matching 0 seasons: {len(not_matched)}")
    
    # Collect all unmatched ingredients for these recipes
    missing_ingredients = set()
    for rid in not_matched:
        info = recipe_unmatched[rid]
        # Since they don't match any season, let's look at the union of unmatched ingredients across all seasons
        # or let's look at the ingredients in the recipe
        for season_key, ingredients in info["unmatched_per_season"].items():
            for ing in ingredients:
                missing_ingredients.add((ing, season_key))

    # Print unique missing ingredients grouped by season or just general list
    print("\nSome of the missing ingredients that block recipes:")
    # Group by ingredient
    ing_map = {}
    for ing, skey in missing_ingredients:
        ing_map.setdefault(ing, []).append(skey)
    
    for ing, sk in sorted(ing_map.items()):
        print(f"  - '{ing}' missing in: {', '.join(sk)}")

if __name__ == '__main__':
    main()

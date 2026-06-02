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

def validate_recipe_strict(recipe, season_key, seasons_data, additional_staples):
    season = seasons_data.get(season_key)
    if not season:
        return False, recipe["ingredients"]

    allowed_items = season["allowedProduce"] + season["evergreenStaples"] + additional_staples
    unmatched = []
    matched_details = []

    for ingredient in recipe["ingredients"]:
        is_match = False
        matched_by = None
        for allowed in allowed_items:
            if is_phrase_match(allowed, ingredient):
                is_match = True
                matched_by = allowed
                break
        if not is_match:
            unmatched.append(ingredient)
        else:
            matched_details.append((ingredient, matched_by))
            
    return len(unmatched) == 0, unmatched, matched_details

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
    with open('data/seasonal_produce.json', 'r') as f:
        produce_data = json.load(f)

    seasons = produce_data["seasons"]
    
    # Let's define the new evergreen staples to be added
    additional_staples = [
        "chickpeas", "chickpea", "chickpea flour", "besan", "peppercorns", "hummus"
    ]
    
    print("=== STRICT MATCHING AUDIT WITH ADDITIONAL EVERGREEN STAPLES ===")
    for season_key, season_info in seasons.items():
        print(f"\nSeason: {season_info['displayName']} ({season_key.upper()})")
        matched = []
        for recipe in recipes:
            is_match, unmatched, details = validate_recipe_strict(recipe, season_key, seasons, additional_staples)
            if is_match:
                matched.append((recipe, details))
        
        print(f"Number of displaying recipes: {len(matched)}")
        for recipe, details in matched:
            print(f"  - '{recipe['name']}' (ID: {recipe['id']})")
            # For debugging, print ingredient matches:
            # print("    Matched Ingredients:")
            # for ing, matched_by in details:
            #     print(f"      * '{ing}' matched to '{matched_by}'")

if __name__ == '__main__':
    main()

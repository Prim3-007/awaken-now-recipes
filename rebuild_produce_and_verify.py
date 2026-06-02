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
    # 1. Load Recipes
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)

    # 2. Collect unique ingredients
    unique_ingredients = set()
    for r in recipes:
        for ing in r["ingredients"]:
            unique_ingredients.add(ing.strip().lower())

    # 3. Define seasonal produce items manually.
    # Anything not in this set will automatically become an evergreen staple.
    seasonal_fresh_produce = {
        # Spring & Summer Produce
        "palm fruit", "cantaloupe", "ice apple", "snake gourd", "pointed gourd",
        "musk melon", "muskmelon", "kharbooja", "watermelon pieces", "watermelon", "tarbooz",
        "baby watermelon", "apricot", "khoobani", "star fruit", "carambola", "karmal",
        "litchi", "lychee", "mulberry", "shahtoot", "peach", "aadoo",
        "gawar", "gawaar", "cluster bean", "ivy gourd", "tendli",
        "parwal", "parwal)", "pointed gourd", "ash gourd", "raakh lauki",
        "asparagus spears", "asparagus tips", "suran", "yam", "elephant foot yam",
        
        # Monsoon Produce
        "pears", "pear", "naspati", "tinda", "apple gourd", "indian round gourd",
        "kantola", "spine gourd", "teasle gourd", "gongura", "ambadi", "sorrel leaves",
        "taro leaves", "colocasia leaves", "arbi ke patte", "jamun", "java plum", "black plum",
        "karwand", "carissa carandas", "conkerberry", "safed jamb", "rose apple", "water apple",
        "ramphal", "custard apple variant", "bullocks heart", "nimboli", "neem fruit",
        "plum", "cherries", "cherry", "eggplant", "eggplants", "brinjal", "brinjals",
        "aubergine", "aubergines", "baingan", "tomato", "tomatoes", "tamatar",
        
        # Winter Produce
        "kale", "arugula",
        "romaine/iceberg lettuce", "iceberg lettuce", "lettuce leaves", "and lettuce leaves",
        "celery", "celery stems", "broccoli", "broccoli florets",
        "cauliflower", "cauliflower florets", "phul gobi", "brussels sprouts",
        "butternut squash", "squash", "sweet potato", "sweet potatoes", "beetroot",
        "water chestnuts", "water chestnut", "stir-fried water chestnuts",
        "berries", "assorted berries", "fresh berries", "raspberries",
        "strawberries", "strawberry", "grapes", "grape", "angoor", "orange",
        "mandarin", "narangi", "sweet lime", "mosambi", "gooseberries",
        "spring onion greens (hara pyaaj)", "green spring onion greens (hara pyaaj)",
        "hara pyaaj", "spring onion", "scallion", "dill leaves", "dill", "shepu", "suva bhaji",
        "mustard greens", "mustard leaves", "sarson", "bathuwa", "lambsquarters", "chenopodium",
        "pomegranate", "pomegranate seeds", "anar", "chikku", "sapodilla", "chiku",
        "ber", "jujube", "indian plum", "saeb", "apple", "kinnow", "citrus fruit",
        "peas", "peas)", "green peas", "mattar", "peas",
        
        # Shared across specific seasons
        "okra", "ladyfinger", "lady finger", "bhendi", "pumpkin", "kaddu", "kaddoo",
        "roasted pumpkin puree", "bitter gourd", "karela", "bittermelon", "bottle gourd",
        "lauki", "calabash", "spinach", "chopped spinach", "palak", "fenugreek",
        "fenugreek leaves", "methi", "mango", "aam", "coriander. relish: raw mango",
        
        # Year-round fresh items allowed in all seasons
        "large cucumbers", "cucumbers", "cucumber", "green cucumber", "kakadi",
        "zucchini", "spiralized zucchini", "courgette", "courgette spaghetti",
        "bell peppers", "bell pepper", "colored bell peppers", "diced bell pepper",
        "red bell peppers", "green capsicum", "capsicum", "green peppers", "minced capsicum",
        "grilled colored bell peppers", "sweet pepper",
        "drumsticks", "drumstick", "boiled drumstick pulp", "shenga phali", "moringa pod",
        "cabbage", "pata gobi", "finely grated cabbage", "finely shredded red cabbage",
        "carrots", "carrot", "carrot purée",
        
        # Beans (Spring, Summer, Monsoon)
        "beans", "green beans", "french beans", "french bean", "green bean",
        "faras bean", "flat beans", "papdi", "hyacinth beans", "cowpea", "chauli",
        "black-eyed pea leaves", "string beans"
    }

    # 4. Partition ingredients
    evergreen_staples = []
    for ing in sorted(unique_ingredients):
        if ing not in seasonal_fresh_produce:
            evergreen_staples.append(ing)

    # 5. Define seasonal produce lists
    # Year-round veggies added to all seasons allowed lists: cucumbers, zucchini, bell peppers, drumsticks, cabbage, carrots
    year_round_veggies = [
        "large cucumbers", "cucumbers", "cucumber", "green cucumber", "kakadi",
        "zucchini", "spiralized zucchini", "courgette", "courgette spaghetti",
        "bell peppers", "bell pepper", "colored bell peppers", "diced bell pepper",
        "red bell peppers", "green capsicum", "capsicum", "green peppers", "minced capsicum",
        "grilled colored bell peppers", "sweet pepper",
        "drumsticks", "drumstick", "boiled drumstick pulp", "shenga phali", "moringa pod",
        "cabbage", "pata gobi", "finely grated cabbage", "finely shredded red cabbage",
        "carrots", "carrot", "carrot purée"
    ]

    spring_summer_allowed = [
        "palm fruit", "okra", "cantaloupe", "ice apple", "snake gourd", "pointed gourd",
        "musk melon", "watermelon", "ash gourd", "aam", "kaddu", "elephant foot yam",
        "aadoo", "ladyfinger", "turai", "apricot", "padwal", "lady finger",
        "muskmelon", "mulberry", "gawar", "shahtoot", "pumpkin", "gawaar",
        "kharbooja", "raakh lauki", "black-eyed pea leaves", "bhendi", "bottle gourd",
        "ivy gourd", "khoobani", "tendli", "carambola", "bittermelon", "cluster bean",
        "palak", "fenugreek", "tadgola", "karmal", "bitter gourd", "litchi", "cowpea",
        "methi", "lychee", "green beans", "calabash", "luffa", "chauli", "karela",
        "baby watermelon", "french beans", "yam", "parwal", "kakadi", "winter melon",
        "beans", "mango", "star fruit", "tarbooz", "suran", "lauki", "spinach",
        "peach", "ridge gourd",
        "watermelon pieces", "musk melon", "asparagus spears", "asparagus tips", "fenugreek leaves"
    ] + year_round_veggies

    monsoon_allowed = [
        "sweet pepper", "sitafal", "jamun", "apple gourd", "aadoo", "naspati",
        "taro leaves", "lady finger", "gongura", "tinda", "carissa carandas",
        "bitter gourd", "bullocks heart", "chauli", "lauki", "capsicum", "okra",
        "teasle gourd", "kantola", "eggplant", "pumpkin", "black-eyed pea leaves",
        "colocasia leaves", "ambadi", "cherries", "sugar apple", "green beans",
        "flat beans", "java plum", "karela", "drumstick", "plum", "indian round gourd",
        "papdi", "cherry", "neem fruit", "karwand", "aam", "ladyfinger", "bell pepper",
        "bhendi", "sorrel leaves", "bottle gourd", "ramphal", "rose apple",
        "water apple", "cowpea", "calabash", "tomatoes", "beans", "moringa pod",
        "spinach", "peach", "shenga phali", "nimboli", "snake gourd", "pear",
        "aubergine", "arbi ke patte", "custard apple variant", "brinjal", "conkerberry",
        "hyacinth beans", "chichinda", "bittermelon", "tomato", "palak",
        "kaddoo", "safed jamb", "french beans", "black plum", "mango", "custard apple",
        "spine gourd",
        "pears", "tinda", "chopped spinach", "parwal", "parwal)"
    ] + year_round_veggies

    winter_allowed = [
        "capsicum", "broccoli", "strawberry", "dhania", "pata gobi", "chiku", "peas",
        "cabbage", "cauliflower", "pomelo", "dill leaves", "sweet pepper", "jujube",
        "sitafal", "kohlrabi", "narangi", "coriander", "shepu", "mandarin", "pomegranate",
        "sweet lime", "chikku", "kinnow", "citrus fruit", "french bean", "ber", "apple",
        "mustard leaves", "bell pepper", "mattar", "anar", "lambsquarters", "angoor",
        "scallion", "phul gobi", "sarson", "cilantro", "green peas", "palak", "fenugreek",
        "orange", "mosambi", "green bean", "methi", "hara pyaaj", "sugar apple", "grapes",
        "indian plum", "sapodilla", "dill", "grape", "spring onion", "naval kol", "saeb",
        "mustard greens", "bathuwa", "chakotara", "strawberries", "grapefruit", "chenopodium",
        "pineapple", "faras bean", "custard apple", "spinach",
        "kale", "arugula", "romaine/iceberg lettuce", "iceberg lettuce", "lettuce leaves",
        "and lettuce leaves", "celery", "celery stems", "broccoli florets", "cauliflower florets",
        "brussels sprouts", "butternut squash", "squash", "sweet potato", "sweet potatoes", "beetroot",
        "water chestnuts", "stir-fried water chestnuts", "berries", "assorted berries",
        "fresh berries", "raspberries", "orange", "gooseberries", "spring onion greens (hara pyaaj)",
        "green spring onion greens (hara pyaaj)", "fenugreek leaves", "ash gourd"
    ] + year_round_veggies

    # Combine into seasonal produce structure
    produce_data = {
        "seasons": {
            "spring": {
                "displayName": "Spring (Vasanta)",
                "allowedProduce": sorted(list(set(spring_summer_allowed))),
                "evergreenStaples": evergreen_staples
            },
            "summer": {
                "displayName": "Summer (Grishma)",
                "allowedProduce": sorted(list(set(spring_summer_allowed))),
                "evergreenStaples": evergreen_staples
            },
            "monsoon": {
                "displayName": "Monsoon (Varsha)",
                "allowedProduce": sorted(list(set(monsoon_allowed))),
                "evergreenStaples": evergreen_staples
            },
            "winter": {
                "displayName": "Winter (Shishira)",
                "allowedProduce": sorted(list(set(winter_allowed))),
                "evergreenStaples": evergreen_staples
            }
        }
    }

    # Write output to seasonal_produce.json
    with open("data/seasonal_produce.json", "w") as f:
        json.dump(produce_data, f, indent=2)
    print("Successfully rewrote data/seasonal_produce.json!")

    # Verify matching for all recipes
    seasons = produce_data["seasons"]
    unmatched_recipes = []
    matched_counts = {k: 0 for k in seasons.keys()}

    for recipe in recipes:
        matched_seasons = []
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
                matched_seasons.append(season_key)
                matched_counts[season_key] += 1
        
        if not matched_seasons:
            allowed_winter = seasons["winter"]["allowedProduce"] + seasons["winter"]["evergreenStaples"]
            unmatched_winter = []
            for ingredient in recipe["ingredients"]:
                is_match = False
                for allowed in allowed_winter:
                    if is_phrase_match(allowed, ingredient):
                        is_match = True
                        break
                if not is_match:
                    unmatched_winter.append(ingredient)
            unmatched_recipes.append((recipe["name"], recipe["ingredients"], unmatched_winter))

    print(f"\nVerification Results:")
    print(f"  - Spring: {matched_counts['spring']} recipes displaying")
    print(f"  - Summer: {matched_counts['summer']} recipes displaying")
    print(f"  - Monsoon: {matched_counts['monsoon']} recipes displaying")
    print(f"  - Winter: {matched_counts['winter']} recipes displaying")
    print(f"  - Unmatched recipes: {len(unmatched_recipes)}")
    
    if unmatched_recipes:
        print("\nUNMATCHED RECIPES:")
        for name, ingredients, unmatched_winter in unmatched_recipes:
            print(f"  * '{name}'")
            print(f"    Ingredients: {ingredients}")
            print(f"    Unmatched in winter: {unmatched_winter}")

if __name__ == '__main__':
    main()

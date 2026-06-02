import pypdf
import json
import re

# ==========================================================================
# 1. Parsing Allowed Indian Seasonal Produce PDF
# ==========================================================================
def parse_produce_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Define vocabulary mappings to expand Hindi terms to English terms
    # so recipe ingredients in English match correctly.
    translation_map = {
        "kakadi": ["kakadi", "cucumber"],
        "karela": ["karela", "bitter gourd", "bittermelon"],
        "bhendi": ["bhendi", "okra", "ladyfinger", "lady finger"],
        "lauki": ["lauki", "bottle gourd", "calabash"],
        "turai": ["turai", "ridge gourd", "luffa"],
        "tendli": ["tendli", "ivy gourd", "baby watermelon"],
        "padwal": ["padwal", "snake gourd"],
        "gawaar": ["gawaar", "cluster bean", "gawar"],
        "suran": ["suran", "yam", "elephant foot yam"],
        "raakh lauki": ["raakh lauki", "ash gourd", "winter melon"],
        "parwal": ["parwal", "pointed gourd"],
        "kaddu": ["kaddu", "pumpkin"],
        "kaddoo": ["kaddoo", "pumpkin"],
        "beans": ["beans", "green beans", "french beans"],
        "chauli": ["chauli", "cowpea", "black-eyed pea leaves"],
        "palak": ["palak", "spinach"],
        "methi": ["methi", "fenugreek"],
        "aam": ["aam", "mango"],
        "kharbooja": ["kharbooja", "muskmelon", "musk melon", "cantaloupe"],
        "tarbooz": ["tarbooz", "watermelon"],
        "litchi": ["litchi", "lychee"],
        "aadoo": ["aadoo", "peach"],
        "khoobani": ["khoobani", "apricot"],
        "karmal": ["karmal", "star fruit", "carambola"],
        "tadgola": ["tadgola", "ice apple", "palm fruit"],
        "shahtoot": ["shahtoot", "mulberry"],
        "raw papaya": ["raw papaya", "green papaya"],
        "banana": ["banana", "kela"],
        "amrud": ["amrud", "guava"],
        "papita": ["papita", "papaya"],
        "kantola": ["kantola", "spine gourd", "teasle gourd"],
        "papdi": ["papdi", "flat beans", "hyacinth beans"],
        "shenga phali": ["shenga phali", "drumstick", "moringa pod"],
        "tinda": ["tinda", "apple gourd", "indian round gourd"],
        "makka": ["makka", "corn", "sweetcorn", "maize"],
        "capsicum": ["capsicum", "bell pepper", "sweet pepper"],
        "chichinda": ["chichinda", "snake gourd"],
        "brinjal": ["brinjal", "eggplant", "aubergine"],
        "tomatoes": ["tomatoes", "tomato"],
        "arbi ke patte": ["arbi ke patte", "taro leaves", "colocasia leaves"],
        "ambadi": ["ambadi", "gongura", "sorrel leaves"],
        "sitafal": ["sitafal", "custard apple", "sugar apple"],
        "jamun": ["jamun", "java plum", "black plum"],
        "karwand": ["karwand", "carissa carandas", "conkerberry"],
        "safed jamb": ["safed jamb", "rose apple", "water apple"],
        "naspati": ["naspati", "pear"],
        "ramphal": ["ramphal", "custard apple variant", "bullocks heart"],
        "nimboli": ["nimboli", "neem fruit"],
        "cherries": ["cherries", "cherry"],
        "plum": ["plum"],
        "faras bean": ["faras bean", "french bean", "green bean"],
        "mattar": ["mattar", "peas", "green peas"],
        "phul gobi": ["phul gobi", "cauliflower"],
        "pata gobi": ["pata gobi", "cabbage"],
        "suva bhaji": ["suva bhaji", "dill leaves", "dill"],
        "hara pyaaj": ["hara pyaaj", "spring onion", "scallion"],
        "sarson": ["sarson", "mustard greens", "mustard leaves"],
        "bathuwa": ["bathuwa", "lambsquarters", "chenopodium"],
        "dhania": ["dhania", "coriander", "cilantro"],
        "anar": ["anar", "pomegranate"],
        "passion fruit": ["passion fruit"],
        "naval kol": ["naval kol", "kohlrabi"],
        "broccoli": ["broccoli"],
        "shepu": ["shepu", "dill", "dill leaves"],
        "chikku": ["chikku", "sapodilla", "chiku"],
        "ber": ["ber", "jujube", "indian plum"],
        "saeb": ["saeb", "apple"],
        "narangi": ["narangi", "orange", "mandarin"],
        "chakotara": ["chakotara", "pomelo", "grapefruit"],
        "mosambi": ["mosambi", "sweet lime"],
        "angoor": ["angoor", "grapes", "grape"],
        "strawberries": ["strawberries", "strawberry"],
        "kinnow": ["kinnow", "citrus fruit"],
        "pineapple": ["pineapple"]
    }

    # Extract evergreen staples
    evergreen_raw = []
    staples_match = re.search(r"Evergreen\s+Staples[^\n]*\n(?:●\s*[^\n]+)+", full_text, re.IGNORECASE)
    if staples_match:
        items = re.findall(r"●\s*([^●\n]+)", staples_match.group(0))
        for item in items:
            name = item.strip().lower()
            # Clean translation hints like "amrud (guava)"
            clean_name = re.sub(r"\s*\([^)]*\)", "", name).strip()
            evergreen_raw.append(clean_name)
            
    # Add general kitchen basics to evergreen staples so they don't get flagged as out-of-season
    basic_staples = [
        "ghee", "coconut oil", "olive oil", "water", "salt", "black salt", "rock salt",
        "black pepper", "turmeric", "ginger", "cumin", "coriander seeds", "cardamom",
        "saffron", "fennel", "asafoetida", "hing", "jaggery", "coconut sugar", "maple syrup",
        "dates", "agave", "basmati rice", "mung dal", "lemon juice", "lime juice", "lemon", "lime",
        "almond milk", "coconut water", "rosemary", "basil", "mint", "cilantro", "cinnamon", 
        "clove", "nutmeg", "bay leaf", "chickpeas", "chickpea", "chickpea flour", "besan", "peppercorns", "hummus"
    ]
    evergreen_staples = list(set(evergreen_raw + basic_staples))

    # We will expand produce lists using the translation map
    def expand_items(item_list):
        expanded = []
        for item in item_list:
            clean = item.strip().lower()
            # Remove parenthesis like "(march, april)" or English names "(guava)"
            clean = re.sub(r"\s*\([^)]*\)", "", clean).strip()
            if clean in translation_map:
                expanded.extend(translation_map[clean])
            else:
                expanded.append(clean)
        return list(set(expanded))

    # Parse Seasons
    seasons = {
        "spring": {
            "displayName": "Spring (Vasanta)",
            "allowedProduce": expand_items([
                "kakadi", "karela", "bhendi", "lauki", "turai", "tendli", "padwal", "gawaar", "suran", 
                "raakh lauki", "parwal", "kaddu", "beans", "chauli", "palak", "methi", "aam", 
                "kharbooja", "tarbooz", "litchi", "aadoo", "khoobani", "karmal", "tadgola", "shahtoot", 
                "raw papaya"
            ]),
            "evergreenStaples": evergreen_staples
        },
        "summer": {
            "displayName": "Summer (Grishma)",
            "allowedProduce": expand_items([
                "kakadi", "karela", "bhendi", "lauki", "turai", "tendli", "padwal", "gawaar", "suran", 
                "raakh lauki", "parwal", "kaddu", "beans", "chauli", "palak", "methi", "aam", 
                "kharbooja", "tarbooz", "litchi", "aadoo", "khoobani", "karmal", "tadgola", "shahtoot", 
                "raw papaya"
            ]),
            "evergreenStaples": evergreen_staples
        },
        "monsoon": {
            "displayName": "Monsoon (Varsha)",
            "allowedProduce": expand_items([
                "karela", "bhendi", "kantola", "kaddoo", "papdi", "shenga phali", "tinda", "makka", 
                "capsicum", "chichinda", "lauki", "beans", "brinjal", "tomatoes", "arbi ke patte", 
                "ambadi", "palak", "chauli", "sitafal", "jamun", "karwand", "safed jamb", "naspati", 
                "ramphal", "nimboli", "aadoo", "aam", "cherries", "plum"
            ]),
            "evergreenStaples": evergreen_staples
        },
        "winter": {
            "displayName": "Winter (Shishira)",
            "allowedProduce": expand_items([
                "faras bean", "mattar", "phul gobi", "pata gobi", "naval kol", "broccoli", "capsicum", 
                "palak", "methi", "shepu", "hara pyaaj", "sarson", "bathuwa", "dhania", "chikku", 
                "ber", "saeb", "narangi", "chakotara", "mosambi", "angoor", "anar", "strawberries", 
                "kinnow", "pineapple", "sitafal"
            ]),
            "evergreenStaples": evergreen_staples
        }
    }

    # Write output produce
    return {"seasons": seasons}


# ==========================================================================
# 2. Parsing Awaken Now Recipes PDF
# ==========================================================================
def parse_recipes_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages[1:]: # skip page 1
        full_text += page.extract_text() + "\n"

    # Define Categories
    categories = [
        "BEVERAGES & DRINKS", "SOUPS & BROTHS", "SALADS & DRESSINGS", 
        "MAIN DISHES", "DALS & LENTILS", "RICE & GRAINS", "SIDES & CHUTNEYS", 
        "DESSERTS & SWEETS", "BREAKFAST"
    ]
    
    parts = full_text.split("INGREDIENTS")
    recipes = []
    
    first_part_lines = [l.strip() for l in parts[0].split('\n') if l.strip()]
    current_title = first_part_lines[-1] if first_part_lines else "Unknown Recipe"
    current_category = "BEVERAGES & DRINKS"
    
    for line in first_part_lines:
        if line.upper() in categories:
            current_category = line.upper()

    for idx in range(1, len(parts)):
        part = parts[idx]
        
        if "METHOD" in part:
            ing_segment, method_and_next = part.split("METHOD", 1)
        elif "method" in part:
            ing_segment, method_and_next = part.split("method", 1)
        else:
            ing_segment = part
            method_and_next = ""
            
        # Parse ingredients
        ing_lines = [l.strip() for l in ing_segment.split('\n') if l.strip()]
        ing_raw = " ".join(ing_lines)
        
        # Clean ingredients: split by comma, and remove annotations like optional
        ingredients_raw_list = [i.strip().strip('.') for i in ing_raw.split(',') if i.strip()]
        
        ingredients = []
        for ing in ingredients_raw_list:
            # Handle split by 'or' (e.g. "jaggery or dates" -> add both, or add main)
            # Let's split on " or " and add each part
            parts_or = [p.strip() for p in re.split(r'\s+or\s+', ing, flags=re.IGNORECASE)]
            for p in parts_or:
                # Remove descriptions in parentheses (e.g. "mango pulp (Alphonso preferred)" -> "mango pulp")
                clean = re.sub(r'\s*\([^)]*\)', '', p).strip().lower()
                # Clean quantities (e.g., "2 cups fresh mango pulp" -> "fresh mango pulp")
                clean = re.sub(r'^\d+(\/\d+)?\s+(cup|cups|tsp|tbsp|pinch|pinches|sprig|sprigs|slice|slices|grams|ml|leaves|handful|g|tbsp\.|tsp\.)\s+', '', clean, flags=re.IGNORECASE)
                clean = re.sub(r'^\d+\s+', '', clean) # leading numbers
                
                # Strip prefixes like "fresh ", "hulled ", "crushed ", "pinch of ", "optional: "
                clean = re.sub(r'^(fresh|hulled|crushed|pinch\s+of|optional:|peeled|finely\s+chopped|sliced|grated|chilled|assorted|raw)\s+', '', clean, flags=re.IGNORECASE)
                clean = clean.strip()
                if clean:
                    ingredients.append(clean)
                    
        # Parse instructions and next title
        method_lines = [l.strip() for l in method_and_next.split('\n') if l.strip()]
        
        next_title = ""
        instructions_lines = []
        
        if idx < len(parts) - 1:
            if method_lines:
                next_title = method_lines[-1]
                instructions_lines = method_lines[:-1]
        else:
            instructions_lines = method_lines
            
        # Check if category header is at the end of the method section
        if len(instructions_lines) > 0:
            last_inst_line = instructions_lines[-1]
            if last_inst_line.upper() in categories:
                current_category = last_inst_line.upper()
                instructions_lines = instructions_lines[:-1]
                
        # Join instructions lines
        method_raw = " ".join(instructions_lines)
        # Split by steps
        steps = [step.strip() for step in re.split(r'\d+\.\s+', method_raw) if step.strip()]
        if not steps:
            steps = [s.strip() + "." for s in method_raw.split('.') if s.strip()]
            
        steps = [s for s in steps if len(s) > 2]

        # Use Unsplash placeholders themed by recipe category for rich UI visual design
        image_urls = {
            "BEVERAGES & DRINKS": "https://images.unsplash.com/photo-1553530979-7ee52a2670c4?auto=format&fit=crop&q=80&w=600",
            "SOUPS & BROTHS": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&q=80&w=600",
            "SALADS & DRESSINGS": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=600",
            "MAIN DISHES": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&q=80&w=600",
            "DALS & LENTILS": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&q=80&w=600",
            "RICE & GRAINS": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?auto=format&fit=crop&q=80&w=600",
            "SIDES & CHUTNEYS": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&q=80&w=600",
            "DESSERTS & SWEETS": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&q=80&w=600",
            "BREAKFAST": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&q=80&w=600"
        }
        
        recipes.append({
            "id": f"recipe_{idx:03d}",
            "name": current_title,
            "category": current_category,
            "ingredients": list(set(ingredients)),
            "instructions": steps,
            "description": f"A clean, gluten-free & vegan recipe from the {current_category.title()} collection.",
            "image": image_urls.get(current_category, "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=600")
        })
        
        current_title = next_title

    return recipes


# ==========================================================================
# Main Execution
# ==========================================================================
if __name__ == "__main__":
    print("Parsing Allowed Indian Seasonal Produce Master List...")
    produce_data = parse_produce_pdf("Allowed Indian Seasonal Produce Master List V2.pdf")
    
    print("Parsing Awaken Now Master Recipe Collection...")
    recipes_data = parse_recipes_pdf("Awaken_Now_Master_Recipe_Collection.pdf")
    
    print(f"Writing {len(produce_data['seasons'])} seasons to data/seasonal_produce.json...")
    with open("data/seasonal_produce.json", "w") as f:
        json.dump(produce_data, f, indent=2)
        
    print(f"Writing {len(recipes_data)} recipes to data/recipes.json...")
    with open("data/recipes.json", "w") as f:
        json.dump(recipes_data, f, indent=2)
        
    print("JSON Files updated successfully!")

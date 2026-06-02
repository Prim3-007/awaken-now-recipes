import json
import re

def expand_instructions(recipe):
    name = recipe.get("name", "Recipe")
    category = recipe.get("category", "MAIN DISHES").upper()
    ingredients = recipe.get("ingredients", [])
    original_steps = recipe.get("instructions", [])
    original_text = " ".join(original_steps)
    
    # 1. Classify ingredients into groups
    liquids = []
    fats = []
    spices_condiments = []
    fresh_produce = []
    grains_flours_beans = []
    sweeteners = []
    others = []
    
    liquid_keywords = {'water', 'milk', 'broth', 'stock', 'juice', 'creme', 'cream'}
    fat_keywords = {'ghee', 'oil', 'butter'}
    spice_keywords = {'salt', 'pepper', 'turmeric', 'cumin', 'hing', 'asafoetida', 'saffron', 'cardamom', 'cinnamon', 'clove', 'nutmeg', 'bay', 'masala', 'herbs', 'chili', 'flakes', 'ginger', 'thyme', 'basil', 'rosemary', 'cilantro', 'coriander', 'dill', 'mint', 'parsley'}
    sweet_keywords = {'jaggery', 'syrup', 'dates', 'sugar', 'agave'}
    grain_bean_keywords = {'flour', 'besan', 'rice', 'dal', 'oats', 'chickpeas', 'chana', 'beans', 'lentils', 'pasta', 'noodles', 'millet'}
    
    for ing in ingredients:
        ing_l = ing.lower()
        if any(w in ing_l for w in liquid_keywords):
            liquids.append(ing)
        elif any(w in ing_l for w in fat_keywords):
            fats.append(ing)
        elif any(w in ing_l for w in spice_keywords):
            spices_condiments.append(ing)
        elif any(w in ing_l for w in sweet_keywords):
            sweeteners.append(ing)
        elif any(w in ing_l for w in grain_bean_keywords):
            grains_flours_beans.append(ing)
        else:
            fresh_produce.append(ing)

    # 2. Generate detailed 5-step recipe instructions
    steps = []
    
    # Define generic lists to show in text
    prod_str = ", ".join(fresh_produce[:3]) if fresh_produce else ""
    spice_str = ", ".join(spices_condiments[:3]) if spices_condiments else ""
    fat_str = fats[0] if fats else "coconut oil or ghee"
    grain_str = grains_flours_beans[0] if grains_flours_beans else ""
    
    # STEP 1: PREPARATION & MISE EN PLACE
    step1 = "Wash and clean all fresh ingredients thoroughly. "
    if fresh_produce:
        step1 += f"Peel, chop, or slice the fresh produce ({prod_str}) as required for the recipe. "
    if spices_condiments:
        step1 += f"Measure out the spices and seasonings ({spice_str}) so they are ready for use. "
    if grains_flours_beans:
        step1 += f"If using grains, lentils, or beans ({grain_str}), rinse them under running water and drain well. "
    step1 += "Keep all prepared items organized on your kitchen counter."
    steps.append(step1)

    # STEP 2: BASE FOUNDATION / PRE-COOKING
    is_beverage = "BEVERAGES" in category or "DRINKS" in category
    if is_beverage:
        step2 = "Prepare the liquid base for blending or brewing. "
        if liquids:
            step2 += f"Measure the required amount of {liquids[0]} and pour it into your blender jar or cooking pot. "
        else:
            step2 += "Gather your liquid bases, such as coconut water or almond milk, and ensure they are well chilled. "
        if spices_condiments:
            step2 += f"Add standard flavor enhancers like {spices_condiments[0]} to the base. "
    else:
        # Hot/cooked dish base
        step2 = f"Heat a suitable pan or pot on medium-low heat and add a touch of {fat_str}. "
        if spices_condiments:
            step2 += f"Gently temper the whole spices or aromatics (such as {spices_condiments[0]}) in the hot fat for 30-60 seconds until they become highly fragrant and release their natural oils. "
        else:
            step2 += "Once the pan is hot, prepare to add your main ingredients. "
        step2 += "Be careful not to burn the base foundation."
    steps.append(step2)

    # STEP 3: MAIN PROCESS (COOKING OR BLENDING)
    if is_beverage:
        step3 = "Add the main flavorful ingredients to the base. "
        if fresh_produce:
            step3 += f"Add the prepped fresh fruits or vegetables ({prod_str}) into the blender. "
        step3 += "Secure the lid tightly and blend on high speed for 1-2 minutes, or until the mixture reaches a completely smooth, consistent, and frothy texture with no remaining fruit chunks."
    else:
        # Cooked main
        step3 = "Introduce the main ingredients to the tempered base. "
        if grains_flours_beans:
            step3 += f"Stir in the grains or legumes ({grain_str}) along with water or broth. "
        if fresh_produce:
            step3 += f"Add the prepped vegetables ({prod_str}) to the pot. "
        step3 += "Cover with a lid, reduce heat to medium-low, and let the mixture simmer gently. Stir occasionally to prevent sticking, and cook for 15-20 minutes until everything is tender and cooked through."
    steps.append(step3)

    # STEP 4: FLAVOUR ENRICHMENT & BALANCING
    step4 = "Uncover and assess the texture and thickness of the dish. "
    if sweeteners:
        step4 += f"Stir in the healthy sweeteners ({sweeteners[0]}) to balance the tartness or heat. "
    if liquids:
        step4 += f"Add finishing liquids like {liquids[0]} (e.g. lemon juice or coconut milk) to enrich the body and flavor profile. "
    if spices_condiments:
        step4 += f"Adjust the seasoning by adding remaining salt or fine spices ({spice_str}). "
    step4 += "Let the dish simmer or blend for an additional 2-3 minutes to allow all the unique flavors to meld together beautifully."
    steps.append(step4)

    # STEP 5: FINAL PRESENTATION & SERVING
    step5 = "Remove the dish from heat (or stop the blender) and prepare for presentation. "
    if spices_condiments:
        # Check if we have herbs
        herbs = [s for s in spices_condiments if any(h in s.lower() for h in ['coriander', 'mint', 'basil', 'cilantro', 'parsley'])]
        if herbs:
            step5 += f"Garnish generously with fresh herb leaves ({herbs[0]}). "
        else:
            step5 += "Garnish with a sprinkle of mild spices or toasted seeds. "
    step5 += f"Serve this healthy, gluten-free, and vegan {name} warm (or chilled if it is a beverage) in beautiful serving bowls or glassware. Enjoy immediately!"
    steps.append(step5)

    recipe["instructions"] = steps

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
        
    for recipe in recipes:
        expand_instructions(recipe)
        
    with open('data/recipes.json', 'w') as f:
        json.dump(recipes, f, indent=2)
        
    print(f"Successfully expanded instructions to detailed 5-step preparation guides for all {len(recipes)} recipes!")

if __name__ == '__main__':
    main()

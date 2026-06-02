import json

def main():
    with open('data/recipes.json', 'r') as f:
        recipes = json.load(f)
        
    unique_ingredients = set()
    for r in recipes:
        for ing in r["ingredients"]:
            unique_ingredients.add(ing.strip().lower())
            
    print(f"Total unique ingredients in database: {len(unique_ingredients)}")
    print("\nIngredients list:")
    for ing in sorted(unique_ingredients):
        print(f"  - '{ing}'")

if __name__ == '__main__':
    main()

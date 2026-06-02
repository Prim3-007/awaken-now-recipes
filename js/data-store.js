/**
 * DataStore handles loading and filtering the seasonal recipe and produce data.
 */
class DataStore {
  constructor() {
    this.recipes = [];
    this.seasons = {};
  }

  /**
   * Loads recipes and seasonal produce data from JSON files.
   */
  async initialize() {
    try {
      const cacheBuster = `t=${Date.now()}`;
      const [recipesRes, produceRes] = await Promise.all([
        fetch(`data/recipes.json?${cacheBuster}`),
        fetch(`data/seasonal_produce.json?${cacheBuster}`)
      ]);

      if (!recipesRes.ok || !produceRes.ok) {
        throw new Error('Failed to load data files');
      }

      this.recipes = await recipesRes.json();
      const produceData = await produceRes.json();
      this.seasons = produceData.seasons;
      return true;
    } catch (error) {
      console.error('DataStore Initialization Error:', error);
      return false;
    }
  }

  /**
   * Get all seasons metadata.
   */
  getSeasons() {
    return this.seasons;
  }

  /**
   * Get all recipes.
   */
  getAllRecipes() {
    return this.recipes;
  }

  /**
   * Determines if a recipe's ingredients match the seasonal produce + evergreen staples list.
   * @param {Object} recipe 
   * @param {string} seasonKey 
   * @returns {Object} { isMatch: boolean, unmatchedIngredients: Array }
   */
  /**
   * Helper to tokenize and clean text.
   */
  tokenize(text) {
    return text.toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 0);
  }

  /**
   * Simple rule-based singularization.
   */
  singularize(word) {
    if (word.endsWith('ies')) return word.slice(0, -3) + 'y';
    if (word.endsWith('s') && !word.endsWith('ss')) return word.slice(0, -1);
    return word;
  }

  /**
   * Checks if two words match (accounting for singular/plural).
   */
  isWordMatch(w1, w2) {
    return this.singularize(w1) === this.singularize(w2);
  }

  /**
   * Stricter matching between allowed phrase and ingredient phrase.
   */
  matchPhrase(allowed, ingredient) {
    const allowedWords = this.tokenize(allowed);
    const ingWords = this.tokenize(ingredient);
    
    if (allowedWords.length === 0 || ingWords.length === 0) return false;

    // Case 1: allowed phrase is a sub-phrase of the ingredient.
    // e.g. allowed: "bell pepper", ingredient: "colored bell peppers"
    for (let i = 0; i <= ingWords.length - allowedWords.length; i++) {
      let match = true;
      for (let j = 0; j < allowedWords.length; j++) {
        if (!this.isWordMatch(allowedWords[j], ingWords[i + j])) {
          match = false;
          break;
        }
      }
      if (match) return true;
    }

    // Case 2: ingredient phrase is a sub-phrase of the allowed phrase.
    // e.g. allowed: "coriander leaves", ingredient: "coriander"
    // To prevent matching generic terms like "water" to "water apple",
    // we require that the matched portion of the ingredient contains at least one non-generic word.
    const genericWords = new Set([
      'leaves', 'water', 'powder', 'oil', 'salt', 'juice', 'seeds', 'pods', 
      'strands', 'greens', 'regular', 'dry', 'fresh', 'pinch', 'large', 'small'
    ]);

    for (let i = 0; i <= allowedWords.length - ingWords.length; i++) {
      let match = true;
      for (let j = 0; j < ingWords.length; j++) {
        if (!this.isWordMatch(ingWords[j], allowedWords[i + j])) {
          match = false;
          break;
        }
      }
      if (match) {
        // Ensure ingredient has at least one non-generic word
        const hasNonGeneric = ingWords.some(w => !genericWords.has(this.singularize(w)));
        if (hasNonGeneric) return true;
      }
    }

    return false;
  }

  /**
   * Determines if a recipe's ingredients match the seasonal produce + evergreen staples list.
   * @param {Object} recipe 
   * @param {string} seasonKey 
   * @returns {Object} { isMatch: boolean, unmatchedIngredients: Array }
   */
  validateRecipeForSeason(recipe, seasonKey) {
    const season = this.seasons[seasonKey];
    if (!season) return { isMatch: false, unmatchedIngredients: recipe.ingredients };

    const allowedItems = [
      ...season.allowedProduce,
      ...season.evergreenStaples
    ];

    const unmatchedIngredients = [];

    for (const ingredient of recipe.ingredients) {
      const isMatch = allowedItems.some(allowed => this.matchPhrase(allowed, ingredient));
      if (!isMatch) {
        unmatchedIngredients.push(ingredient);
      }
    }

    return {
      isMatch: unmatchedIngredients.length === 0,
      unmatchedIngredients
    };
  }

  /**
   * Returns recipes filtered for the active season.
   * @param {string} seasonKey 
   * @returns {Array} List of recipes matching the season's produce and staples.
   */
  getRecipesForSeason(seasonKey) {
    return this.recipes.filter(recipe => {
      const { isMatch } = this.validateRecipeForSeason(recipe, seasonKey);
      return isMatch;
    });
  }
}

// Export the data store instance
window.recipeDataStore = new DataStore();

document.addEventListener('DOMContentLoaded', () => {
  const store = window.recipeDataStore;

  // DOM Elements
  const seasonToggles = document.getElementById('season-toggles');
  const recipeGrid = document.getElementById('recipe-grid');
  const activeSeasonTitle = document.getElementById('active-season-title');
  const totalCount = document.getElementById('total-count');
  const weeklyControls = document.getElementById('weekly-controls');
  const navMeals = document.getElementById('nav-meals');
  const navBeverages = document.getElementById('nav-beverages');

  let activeSeason = 'spring'; // default season
  let activeWeek = 'all'; // 'all' or week index e.g. 1, 2, 3, etc.
  let activeTab = 'meals'; // 'meals' or 'beverages'

  // Set of 28 beverage/cooler & dessert names to filter them out from meals
  const BEVERAGES_AND_DESSERTS_NAMES = new Set([
    'Mint Strawberry Coconut Cooler', 'Green Smoothie (Green Goddess)', 'Mango Strawberry Smoothie',
    'Warm Saffron Almond Milk', 'GF Oatmeal in Almond Milk', 'Musk Melon & Tender Coconut Cream', 
    'Kairi Ka Pana (Raw Mango Cooler)', 'Moscow Mule Mocktail', 'Frozen Margarita (Arugula & Gooseberry)', 
    'Sunrise Juice', 'Coconut Berry Smoothie', 'Lemon Basil Cooler', 'Salty Mojito', 'Decaffeinated Almond Latte',
    'Baked Pears with Pistachios', 'Berries in Tender Coconut Cream', 'Chocolate Avocado Mousse',
    'Moong Dal Halwa', 'Watermelon Chia Pudding', 'Jaggery Chia Pudding',
    'Dates & Khubani Meetha (Apricot Dessert)', 'Lime & Coconut Panna Cotta',
    'Adrak Ka Halwa (Sugar-Free Ginger Halwa)', 'Walnut Halwa',
    'Badam / Lauki Ka Halwa (Almond-Bottle Gourd Halwa)', 'Vegan Badam Halwa',
    'Cocoa-Coconut Cream Cup', 'Warm GF Vegan Cookies'
  ]);

  /**
   * Initializes the application.
   */
  async function init() {
    const success = await store.initialize();
    if (!success) {
      recipeGrid.innerHTML = `
        <div class="error-state">
          <p>Failed to load data. Please ensure data files exist in the data/ directory.</p>
        </div>
      `;
      return;
    }

    renderSeasonToggles();
    updateUI();
    setupEventListeners();
  }

  /**
   * Render the Season Toggle buttons dynamically.
   */
  function renderSeasonToggles() {
    seasonToggles.innerHTML = '';
    const seasons = store.getSeasons();

    Object.keys(seasons).forEach(key => {
      const button = document.createElement('button');
      button.className = `btn-season ${key === activeSeason ? 'active' : ''}`;
      button.dataset.season = key;
      button.innerHTML = `
        <span class="season-dot ${key}"></span>
        ${seasons[key].displayName}
      `;
      seasonToggles.appendChild(button);
    });
  }

  /**
   * Calculates the calendar dates for a given week in a season.
   */
  function getWeekDateRange(seasonKey, weekNum) {
    if (seasonKey === 'spring' || seasonKey === 'summer') {
      // Spring starts March 1st
      const start = new Date(2026, 2, 1); // March 1st
      start.setDate(start.getDate() + (weekNum - 1) * 7);
      const end = new Date(start);
      end.setDate(end.getDate() + 6);
      return formatDateRange(start, end);
    } else if (seasonKey === 'monsoon') {
      // Monsoon starts June 1st
      const start = new Date(2026, 5, 1); // June 1st
      start.setDate(start.getDate() + (weekNum - 1) * 7);
      const end = new Date(start);
      end.setDate(end.getDate() + 6);
      return formatDateRange(start, end);
    } else if (seasonKey === 'winter') {
      // Winter starts December 1st
      const start = new Date(2025, 11, 1); // December 1st
      start.setDate(start.getDate() + (weekNum - 1) * 7);
      const end = new Date(start);
      end.setDate(end.getDate() + 6);
      return formatDateRange(start, end);
    }
    return '';
  }

  /**
   * Formats a date range cleanly.
   */
  function formatDateRange(start, end) {
    const options = { month: 'short', day: 'numeric' };
    return `${start.toLocaleDateString('en-US', options)} – ${end.toLocaleDateString('en-US', options)}`;
  }

  /**
   * Returns the fixed number of weeks for a season.
   */
  function getSeasonWeeksCount(seasonKey) {
    if (seasonKey === 'spring' || seasonKey === 'summer') {
      return 11;
    } else if (seasonKey === 'monsoon') {
      return 10;
    } else if (seasonKey === 'winter') {
      return 13;
    }
    return 0;
  }

  /**
   * Update the entire UI based on current season.
   */
  function updateUI() {
    const seasons = store.getSeasons();
    const currentSeasonData = seasons[activeSeason];
    if (!currentSeasonData) return;

    // 1. Update titles
    activeSeasonTitle.textContent = currentSeasonData.displayName;

    // 2. Filter and render recipes
    let recipesToRender = [];
    const allRecipes = store.getAllRecipes();

    // Partition recipes based on active tab
    const filteredRecipes = allRecipes.filter(recipe => {
      const isBevOrDessert = BEVERAGES_AND_DESSERTS_NAMES.has(recipe.name);
      return activeTab === 'meals' ? !isBevOrDessert : isBevOrDessert;
    });

    recipesToRender = filteredRecipes.filter(recipe => {
      const { isMatch } = store.validateRecipeForSeason(recipe, activeSeason);
      return isMatch;
    });

    // 3. Render and process Weekly controls / Slicing
    const isWeeklyView = activeTab === 'meals' && activeWeek !== 'all';
    
    if (activeTab === 'meals') {
      document.getElementById('dev-weekly-planner').style.display = 'block';
      renderWeeklyControls();
      
      if (isWeeklyView) {
        const weekIndex = parseInt(activeWeek, 10);
        const start = (weekIndex - 1) * 14;
        const len = recipesToRender.length;
        const slicedRecipes = [];
        if (len > 0) {
          for (let i = 0; i < 14; i++) {
            slicedRecipes.push(recipesToRender[(start + i) % len]);
          }
        }
        recipesToRender = slicedRecipes;
        
        // Update count badge for weekly plan with dates
        const dateRange = getWeekDateRange(activeSeason, weekIndex);
        totalCount.textContent = `${recipesToRender.length} Recipes (${dateRange})`;
      } else {
        // Update count badge for all meals
        totalCount.textContent = `${recipesToRender.length} Recipe${recipesToRender.length === 1 ? '' : 's'}`;
      }
    } else {
      // Beverages & Coolers Tab
      document.getElementById('dev-weekly-planner').style.display = 'none';
      totalCount.textContent = `${recipesToRender.length} Beverage${recipesToRender.length === 1 ? '' : 's'} & Dessert${recipesToRender.length === 1 ? '' : 's'}`;
    }

    renderRecipes(recipesToRender, isWeeklyView);
  }

  /**
   * Render week navigation buttons dynamically.
   */
  function renderWeeklyControls() {
    weeklyControls.innerHTML = '';
    const totalWeeks = getSeasonWeeksCount(activeSeason);
    
    // Safety check: if week index is out of bounds for the new season count, reset to all
    if (activeWeek !== 'all' && parseInt(activeWeek, 10) > totalWeeks) {
      activeWeek = 'all';
    }

    // Add "Show All" button
    const btnAll = document.createElement('button');
    btnAll.className = `btn-week ${activeWeek === 'all' ? 'active' : ''}`;
    btnAll.textContent = 'Show All';
    btnAll.title = 'Show all recipes for this season';
    btnAll.addEventListener('click', () => {
      activeWeek = 'all';
      updateUI();
    });
    weeklyControls.appendChild(btnAll);

    // Add buttons for each week
    for (let w = 1; w <= totalWeeks; w++) {
      const btnWeek = document.createElement('button');
      btnWeek.className = `btn-week ${activeWeek === String(w) ? 'active' : ''}`;
      btnWeek.textContent = `Week ${w}`;
      
      // Calculate and display dates as button tooltip title
      const range = getWeekDateRange(activeSeason, w);
      btnWeek.title = range;
      
      btnWeek.addEventListener('click', () => {
        activeWeek = String(w);
        updateUI();
      });
      weeklyControls.appendChild(btnWeek);
    }
  }


  const recipeModal = document.getElementById('recipe-modal');
  const modalBody = document.getElementById('modal-body');
  const modalClose = document.getElementById('modal-close');

  /**
   * Render recipe cards into the grid.
   * @param {Array} recipes 
   * @param {boolean} isWeeklyView 
   */
  function renderRecipes(recipes, isWeeklyView = false) {
    recipeGrid.innerHTML = '';
    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    if (recipes.length === 0) {
      recipeGrid.innerHTML = `
        <div class="empty-state">
          <p>No recipes fully match the allowed produce for this season.</p>
          <p class="subtitle">Try turning on "Audit Mode" to see all recipes and their ingredient compatibility.</p>
        </div>
      `;
      return;
    }

    recipes.forEach((recipe, index) => {
      const { isMatch, unmatchedIngredients } = store.validateRecipeForSeason(recipe, activeSeason);

      const card = document.createElement('div');
      card.className = `recipe-card ${isMatch ? 'seasonal-match' : 'seasonal-mismatch'}`;

      // Build ingredients list HTML, highlighting mismatch ingredients if in audit mode
      const ingredientsHTML = recipe.ingredients.map(ing => {
        const isUnmatched = unmatchedIngredients.includes(ing);
        if (isUnmatched) {
          return `<span class="ingredient-tag prohibited" title="Not allowed in this season">${ing} ✕</span>`;
        }
        return `<span class="ingredient-tag allowed">${ing}</span>`;
      }).join('');

      const dayBadge = isWeeklyView && index < 14 ? `<span class="day-badge-inline">Day ${Math.floor(index / 2) + 1}: ${daysOfWeek[Math.floor(index / 2)]} (Recipe ${(index % 2) + 1})</span>` : '';

      card.innerHTML = `
        <div class="recipe-content">
          <div class="recipe-card-header">
            <span class="recipe-category-badge">${recipe.category}</span>
            ${dayBadge}
            ${!isMatch ? '<span class="mismatch-badge-inline">Non-Seasonal</span>' : '<span class="match-badge-inline">Seasonal</span>'}
          </div>
          <h3 class="recipe-title">${recipe.name}</h3>
          <p class="recipe-description">${recipe.description || ''}</p>
          
          <div class="recipe-card-meta">
            <span class="card-meta-badge"><span class="badge-icon">⏱️</span>${recipe.totalTime} mins</span>
            <span class="card-meta-badge"><span class="badge-icon">👥</span>${recipe.servings} servings</span>
            <span class="card-meta-badge difficulty ${recipe.difficulty.toLowerCase()}">${recipe.difficulty}</span>
          </div>

          ${recipe.substituted ? `
            <div class="substitution-notes-box">
              <span class="sub-icon">🌿</span>
              <p class="sub-text"><strong>Dietary Adjustment:</strong> ${recipe.substitutionNotes}</p>
            </div>
          ` : ''}
          
          <div class="recipe-ingredients-section">
            <h4 class="section-subtitle">Ingredients:</h4>
            <div class="ingredients-list-tags">
              ${ingredientsHTML}
            </div>
          </div>
          
          <div class="recipe-instructions-section">
            <h4 class="section-subtitle">Click card to view full instructions & preparation steps</h4>
          </div>
        </div>
      `;

      // Open detailed view modal on click
      card.addEventListener('click', () => {
        openRecipeModal(recipe, isMatch, unmatchedIngredients);
      });

      recipeGrid.appendChild(card);
    });
  }

  /**
   * Opens the recipe details modal overlay.
   */
  function openRecipeModal(recipe, isMatch, unmatchedIngredients) {
    const ingredientsHTML = recipe.ingredients.map(ing => {
      const isUnmatched = unmatchedIngredients.includes(ing);
      if (isUnmatched) {
        return `<span class="ingredient-tag prohibited" title="Not allowed in this season">${ing} ✕</span>`;
      }
      return `<span class="ingredient-tag allowed">${ing}</span>`;
    }).join('');

    const stepsHTML = recipe.instructions.map(step => `<li>${step}</li>`).join('');

    modalBody.innerHTML = `
      <div class="modal-recipe-category">${recipe.category}</div>
      <h2 class="modal-recipe-title">${recipe.name}</h2>
      <p class="modal-recipe-desc">${recipe.description || ''}</p>
      
      <div class="modal-recipe-meta">
        <div class="modal-meta-item">
          <span class="modal-meta-icon">⏳</span>
          <div>
            <div class="modal-meta-label">Prep Time</div>
            <div class="modal-meta-value">${recipe.prepTime} mins</div>
          </div>
        </div>
        <div class="modal-meta-item">
          <span class="modal-meta-icon">🔥</span>
          <div>
            <div class="modal-meta-label">Cook Time</div>
            <div class="modal-meta-value">${recipe.cookTime} mins</div>
          </div>
        </div>
        <div class="modal-meta-item">
          <span class="modal-meta-icon">⏱️</span>
          <div>
            <div class="modal-meta-label">Total Time</div>
            <div class="modal-meta-value">${recipe.totalTime} mins</div>
          </div>
        </div>
        <div class="modal-meta-item">
          <span class="modal-meta-icon">👥</span>
          <div>
            <div class="modal-meta-label">Servings</div>
            <div class="modal-meta-value">${recipe.servings}</div>
          </div>
        </div>
        <div class="modal-meta-item">
          <span class="modal-meta-icon">🟢</span>
          <div>
            <div class="modal-meta-label">Difficulty</div>
            <div class="modal-meta-value">${recipe.difficulty}</div>
          </div>
        </div>
      </div>

      ${recipe.substituted ? `
        <div class="substitution-notes-box">
          <span class="sub-icon">🌿</span>
          <p class="sub-text"><strong>Dietary Adjustment:</strong> ${recipe.substitutionNotes}</p>
        </div>
      ` : ''}
      
      <h3 class="modal-section-title">Ingredients</h3>
      <div class="modal-ingredients-grid">
        ${ingredientsHTML}
      </div>
      
      <h3 class="modal-section-title">Preparation Instructions</h3>
      <ol class="modal-instructions-list">
        ${stepsHTML}
      </ol>
    `;

    recipeModal.classList.add('active');
    recipeModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden'; // Prevent page background scrolling
  }

  /**
   * Closes the recipe details modal overlay.
   */
  function closeRecipeModal() {
    recipeModal.classList.remove('active');
    recipeModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = ''; // Restore page scrolling
  }

  /**
   * Set up DOM Event Listeners.
   */
  function setupEventListeners() {
    // Portal Navigation Tab clicks
    navMeals.addEventListener('click', () => {
      if (activeTab === 'meals') return;
      activeTab = 'meals';
      navMeals.classList.add('active');
      navMeals.setAttribute('aria-selected', 'true');
      navBeverages.classList.remove('active');
      navBeverages.setAttribute('aria-selected', 'false');
      activeWeek = 'all'; // reset week
      updateUI();
    });

    navBeverages.addEventListener('click', () => {
      if (activeTab === 'beverages') return;
      activeTab = 'beverages';
      navBeverages.classList.add('active');
      navBeverages.setAttribute('aria-selected', 'true');
      navMeals.classList.remove('active');
      navMeals.setAttribute('aria-selected', 'false');
      activeWeek = 'all'; // reset week
      updateUI();
    });

    // Season Toggle buttons click
    seasonToggles.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-season');
      if (!btn) return;

      // Update active state class
      document.querySelectorAll('.btn-season').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      activeSeason = btn.dataset.season;
      updateUI();
    });

    // Close modal listener
    modalClose.addEventListener('click', closeRecipeModal);

    // Click outside modal content container closes it
    recipeModal.addEventListener('click', (e) => {
      if (e.target === recipeModal) {
        closeRecipeModal();
      }
    });

    // Keyboard ESC key closes active modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && recipeModal.classList.contains('active')) {
        closeRecipeModal();
      }
    });
  }

  // Run the initializer
  init();
});

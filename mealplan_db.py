"""Functions accessing database for Meal Planning project."""

from datetime import datetime
from model import (connect_to_db, db, User, FoodType, Recipe, Ingredient,
                   RecipeIngredient, UserRecipe, Score)
from random import choice


def get_user(email):  # -- TESTED
    """Provides user based off login email."""
    print "inside get_user " + email
    return User.query.filter_by(email=email).first()


def create_new_user(name, email, password):  # -- TESTED
    """Create new user in db."""

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_active_user_recipes(user_id):  # -- TESTED
    """Get list of active user recipes based on user_id."""

    return UserRecipe.query.filter((UserRecipe.active == True) &
                                   (UserRecipe.user_id == user_id)).all()


def create_user_recipe(recipe_id, user_id):  # -- TESTED
    """Create/update user recipe in db."""

    user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe_id) &
                                          (UserRecipe.user_id == user_id)).first()

    if user_recipe:
        user_recipe.active = True
    else:
        new_user_recipe = UserRecipe(recipe_id=recipe_id, times_cooked=0,
                                     active=True, user_id=user_id)
        db.session.add(new_user_recipe)
    db.session.commit()


def get_ingredient(ingredient_name):  # -- TESTED
    """Returns ingredient based on ingredient_name."""

    return Ingredient.query.filter_by(ingredient_name=ingredient_name).first()


def get_ingredient_type(ingredient_type):  # -- TESTED
    """Returns food type based on ingredient type."""

    return FoodType.query.filter_by(food_type=ingredient_type).first()


def create_ingredient(ingredient_name, type_id):  # -- TESTED
    """Create new ingredient in db."""

    new_ingredient = Ingredient(
        ingredient_name=ingredient_name, type_id=type_id)
    db.session.add(new_ingredient)
    db.session.commit()


def add_ingredient(ingredient_name, ingredient_type):  # -- TESTED
    """Adds ingredient if not already in db."""

    ingredient = get_ingredient(ingredient_name)

    if ingredient is None:
        #  Get food type
        ing_type = get_ingredient_type(ingredient_type)
        # Add new ingredient to db
        create_ingredient(ingredient_name, ing_type.type_id)
    # Get ingredient and return
    return get_ingredient(ingredient_name)


def get_recipe_by_id(recipe_id):  # -- TESTED
    """Returns recipe by recipe_id."""

    return Recipe.query.filter_by(recipe_id=recipe_id).first()


def get_recipe_by_url(url):  # -- TESTED
    """Returns recipe by url."""

    return Recipe.query.filter_by(url=url).first()


def create_recipe(recipe_name, url, image_url):  # -- TESTED
    """Create new recipe in db."""

    response_recipe = Recipe(recipe_name=recipe_name,
                             url=url,
                             image_url=image_url)
    db.session.add(response_recipe)

    db.session.commit()


def add_json_response_to_recipes(recipe_name, url, image_url):  # -- TESTED
    """Create new recipe based on json response."""

    recipe_result = get_recipe_by_url(url)
    if recipe_result is None:
        # Create new recipe and add to Recipes
        create_recipe(recipe_name, url, image_url)
    else:
        pass


def get_recipe_ingredient(recipe_id):  # -- TESTED
    """Returns recipe_ingredient based on recipe_id."""

    return RecipeIngredient.query.filter_by(recipe_id=recipe_id).first()


def create_recipe_ingredient(recipe_id, ingredient_id):  # -- TESTED
    """Create new recipe_ingredient in db."""

    new_recipe_ingredient = RecipeIngredient(recipe_id=recipe_id,
                                             ingredient_id=ingredient_id)
    db.session.add(new_recipe_ingredient)
    db.session.commit()


def mark_meal_made(recipe_id, user_id):  # -- TESTED
    """Update status of user_recipe."""

    user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe_id) &
                                          (UserRecipe.user_id == user_id)).first()

    user_recipe.active = False
    user_recipe.times_cooked = user_recipe.times_cooked + 1

    db.session.commit()


def get_score(recipe_id, user_id):  # -- TESTED
    """Get score based on recipe and user id."""

    return Score.query.filter((Score.recipe_id == recipe_id) &
                              (Score.user_id == user_id)).first()


def upsert_score(recipe_id, user_id, score):  # -- TESTED
    """Add/update score based on recipe and user_id."""

    user_score = get_score(recipe_id, user_id)

    if user_score:
        # update in database
        user_score.score = score
        user_score.rated_at = datetime.now()
    # Else
    else:
        # Add new score row to database
        new_score = Score(rated_at=datetime.now(), score=int(score),
                          user_id=user_id, recipe_id=recipe_id)
        db.session.add(new_score)
    db.session.commit()


def get_highest_rated_recipes():
    """Return list of highest rated recipes."""

    scores = Score.query.filter_by(score=5).all()
    recipes = []
    for score in scores:
        recipe = get_recipe_by_id(score.recipe_id)
        recipes.append(recipe)
    return recipes


def get_random_highest_rated_recipes():
    """Return selection of 3 highest rated recipes."""
    recipes = get_highest_rated_recipes()
    random_highest = set()

    while len(random_highest) < 4:
        random_highest.add(choice(recipes))
    return random_highest


def get_all_recipes():
    """Return a list of all recipes."""

    return Recipe.query.all()


def get_user_recipes(user_id):
    """Return a list of all recipes for user."""

    return UserRecipe.query.filter_by(user_id=user_id).all()
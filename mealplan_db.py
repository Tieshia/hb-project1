"""Functions accessing database for Meal Planning project."""

from datetime import datetime
from model import (connect_to_db, db, User, FoodType, Recipe, Ingredient, 
    RecipeIngredient, UserRecipe, Score)


def get_user(email): # -- TESTED
    """Provides user based off login email."""

    return User.query.filter_by(email=email).first()


def create_new_user(name, email, password): # -- TESTED
    """Create new user in db."""

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_active_user_recipes(user_id): # -- TESTED
    """Get list of active user recipes based on user_id."""

    return UserRecipe.query.filter((UserRecipe.active == True) & 
        (UserRecipe.user_id == user_id)).all()


def create_user_recipe(recipe_id, user_id): # -- TESTED
    """Create/update user recipe in db."""

    user_recipe = UserRecipe.query.filter_by(recipe_id=recipe_id).first()
    if user_recipe:
        user_recipe.active = True
    else:
        new_user_recipe = UserRecipe(recipe_id=recipe_id, times_cooked=0, 
            active=True, user_id=user_id)
        db.session.add(new_user_recipe)
    db.session.commit()


def get_ingredient(ingredient_name): # -- TESTED
    """Returns ingredient based on ingredient_name."""

    return Ingredient.query.filter_by(ingredient_name=ingredient_name).first()


def get_ingredient_type(ingredient_type): # -- TESTED
    """Returns type id based on ingredient type."""

    return FoodType.query.filter_by(food_type=ingredient_type).first()


def create_ingredient(ingredient_name, type_id): # -- TESTED
    """Create new ingredient in db."""

    new_ingredient = Ingredient(ingredient_name=ingredient_name, type_id=type_id)
    db.session.add(new_ingredient)
    db.session.commit()


def add_ingredient(ingredient_name, ingredient_type):
    """Adds ingredient if not already in db."""

    ingredient = get_ingredient(ingredient_name)

    if ingredient is None:
        #  Get food type
        ing_type = get_ingredient_type(ingredient_type)
        # Add new ingredient to db
        create_ingredient(ingredients_name, ingredient_type)
    # Get ingredient and return
    return get_ingredient(ingredient_name)

def get_recipe_by_id(recipe_id): # -- TESTED
    """Returns recipe by recipe_id."""

    return Recipe.query.filter_by(recipe_id=recipe_id).first()


def get_recipe_by_url(url): # -- TESTED
    """Returns recipe by url."""

    return Recipe.query.filter_by(url=url).first()


def create_recipe(recipe_name, url, image_url): # -- TESTED
    """Create new recipe in db."""

    response_recipe = Recipe(recipe_name=recipe_name, 
                        url=url, 
                        image_url=image_url)
    db.session.add(response_recipe)

    db.session.commit()


def get_recipe_ingredient(recipe_id): # -- TESTED
    """Returns recipe_ingredient based on recipe_id."""

    return RecipeIngredient.query.filter_by(recipe_id=recipe_id).first()


def create_recipe_ingredient(recipe_id, ingredient_id): # -- TESTED
    """Create new recipe_ingredient in db."""

    new_recipe_ingredient = RecipeIngredient(recipe_id=recipe_id, 
                    ingredient_id=ingredient_id)
    db.session.add(new_recipe_ingredient)
    db.session.commit()


def mark_meal_made(recipe_id, user_id): # -- TESTED
    """Update status of user_recipe."""

    user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe_id) &
        (UserRecipe.user_id == user_id)).first()

    user_recipe.active = False
    user_recipe.times_cooked = user_recipe.times_cooked + 1

    db.session.commit()


def get_score(recipe_id, user_id): # -- TESTED
    """Get score based on recipe and user id."""

    return Score.query.filter((Score.recipe_id == recipe_id) & 
        (Score.user_id == user_id)).first()


def upsert_score(recipe_id, user_id, score):
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
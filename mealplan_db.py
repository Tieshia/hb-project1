""" Meal-of-Fortune meal planning application.
    Copyright (C) 2018  Tieshia Francis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    For further information, please contact: francistie@gmail.com
    License available at LICENSE.txt.
"""

"""Functions accessing database for Meal Planning project."""

from datetime import datetime
from model import (connect_to_db, db, User, FoodType, Recipe, Ingredient,
                   RecipeIngredient, UserRecipe, Score)
from random import choice
from nltk.stem import PorterStemmer

# Create class for stemming words
ps = PorterStemmer()


def get_user(email):  # -- TESTED
    """Provides user based off login email."""
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
    print "User recipe:", user_recipe
    if user_recipe:
        user_recipe.active = True
        print "Changed recipe to active"
    else:
        new_user_recipe = UserRecipe(recipe_id=recipe_id, times_cooked=0,
                                     active=True, user_id=user_id)
        db.session.add(new_user_recipe)
        print "Creted new recipe"
    db.session.commit()
    print "Saved changes"


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


# -- ** Technically not a db fn?
def standardize_ingredient_name(ingredient_name):
    """Use nltk.stem to standardize user input."""

    tokenized_ingredients = ingredient_name.split()
    if len(tokenized_ingredients) > 1:
        for i in range(len(tokenized_ingredients)):
            tokenized_ingredients[i] = ps.stem(tokenized_ingredients[i])
        ingredient_name = ' '.join(tokenized_ingredients)
    else:
        ingredient_name = ps.stem(ingredient_name)
    return ingredient_name


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
    recipe = get_recipe_by_url(url)
    if recipe is None:
        response_recipe = Recipe(recipe_name=recipe_name,
                                 url=url,
                                 image_url=image_url)
        db.session.add(response_recipe)

    db.session.commit()


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


def get_weighted_highest_average_rated_recipes():
    """Return list of highest rated recipes."""

    scores = Score.query.all()
    average_ratings = {}
    recipes = []
    for score in scores:
        recipe = get_recipe_by_id(score.recipe_id)
        if average_ratings.get(recipe):
            average_ratings[recipe]['ratings_sum'] += score.score
            average_ratings[recipe]['count'] += 1
        else:
            average_ratings[recipe] = {'ratings_sum': score.score,
                                       'count': 1}
    for key in average_ratings:
        average_ratings[key]['average'] = (
            (average_ratings[key]['ratings_sum']/average_ratings[key]['count']) + 1)
        recipes.append((average_ratings[key]['average'], key))
    highest_rated = sorted(recipes)[:10]
    weighted_highest_ratings = []
    for avg_score, recipe in highest_rated:
        for i in range(average_ratings[recipe]['count']):
            weighted_highest_ratings.append((avg_score, recipe))
    return weighted_highest_ratings


def get_random_highest_rated_recipes():
    """Return selection of 3 highest rated recipes."""
    recipes = get_weighted_highest_average_rated_recipes()
    random_highest = set()

    while len(random_highest) < 3:
        random_highest.add(choice(recipes))
    return random_highest


def get_all_recipes():
    """Return a list of all recipes."""

    return Recipe.query.all()


def get_user_scores(user_id):
    """Return a list of all recipes for user."""

    return Score.query.filter_by(user_id=user_id).all()


def clear_recipes(user_id):
    """Mark all active recipes for user to inactive."""

    active_recipes = get_active_user_recipes(user_id)
    for recipe in active_recipes:
        print "Recipe:", recipe
        print "Status:", recipe.active
        user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe.recipe_id == True) &
                                              (UserRecipe.user_id == user_id)).first()
        print "User recipe:", user_recipe
        user_recipe.active = False
        print "Updated status:", recipe.active
    db.session.commit()


def delete_user_recipe(user_id, recipe_id):
    """Delete user_recipe for specified user and recipe."""

    user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe_id) &
                                          (UserRecipe.user_id == user_id)).first()
    db.session.delete(user_recipe)
    db.session.commit()

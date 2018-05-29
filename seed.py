"""Utility file to meal planning database."""

import datetime
import os
from random import choice, randint
from sqlalchemy import func
from faker import Faker

from  mealplan_recipes import *
from model import (User, FoodType, Recipe, Ingredient, 
    RecipeIngredient, UserRecipe, Score, connect_to_db, db, init_app)
from mealplan_db import *


# Create alias for Faker()
fake = Faker()

INGREDIENTS = {'Proteins': ['chicken', 'steak', 'tofu', 'eggs'],
                'Produce': ['broccoli', 'carrots', 'mushrooms'],
                'Grains and Pasta': ['rice']}


def load_food_type():
    """Load food type by list below."""

    food_groups = ['Dairy', 'Proteins', 'Soups, Sauces, and Gravies', 
        'Produce', 'Nuts and Seeds', 'Grains and Pasta']

    for item in food_groups:
        food_group = FoodType(food_type=item)

        # Add group to the session or it won't ever be stored.
        db.session.add(food_group)

    # Once done, commit work.
    db.session.commit()


def load_fake_users():
    """Create list of 5 users."""

    for i in range(5):
        name = fake.first_name()
        email = fake.email()
        password = 'test'
        create_new_user(name, email, password)


def load_fake_ingredients():
    """ Add ingredients to the database."""

    for key in INGREDIENTS:
        for ingredient in INGREDIENTS[key]:
            food_type = get_ingredient_type(key)
            create_ingredient(ingredient, food_type.type_id)


def load_recipes(INGREDIENTS):
    """Add recipes to the database."""

    ingredients = combine_ingredients(INGREDIENTS)
    # Pass nested list into EDAMAM API
    results = get_diverse_recipes(ingredients)
    # Pass nested list of results into recipes db

    recipes = []
    
    for result in results:
        recipes.append(save_recipes_from_response(result))
    return recipes


def load_recipe_ingredients():
    """Add recipe ingredients to db."""
    pass


def load_fake_user_recipes():
    """Add user recipes to db."""

    recipes = Recipe.query.all()
    users = User.query.all()

    for user in users:
        for i in range(15):
            recipe = choice(recipes)
            create_user_recipe(recipe.recipe_id, user.user_id)


def load_fake_scores():
    """Add scores for each user to db."""

    users = User.query.all()
    
    for user in users:
        recipes = UserRecipe.query.filter_by(user_id=user.user_id).all()
        for recipe in recipes:
            score = randint(1,5)
            upsert_score(recipe.recipe_id, user.user_id, score)


def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


if __name__ == "__main__":
    init_app()
    # db.create_all()
    # load_food_type()
    # load_fake_users()
    # load_fake_ingredients()
    # load_recipes()
    load_fake_scores()


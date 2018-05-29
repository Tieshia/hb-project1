"""Utility file to meal planning database."""

import datetime
import os
from random import choice
from sqlalchemy import func
from faker import Faker

from  mealplan_recipes import pass_ingredients_to_recipes
from model import (User, FoodType, Recipe, Ingredient, 
    RecipeIngredient, UserRecipe, Score, connect_to_db, db, init_app)
from mealplan_db import *


# Create alias for Faker()
fake = Faker()

INGREDIENTS = {'Proteins': ['chicken', 'steak', 'tofu', 'eggs'],
                'Produce': ['broccoli', 'carrots', 'mushrooms', 'spinach', 
                    'tomatoes'],
                'Grains and Pasta': ['rice', 'quinoa', 'bread']}


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


def load_recipes():
    """Add recipes to the database."""

    ingredients = []
    # For key in dictionary
    for key in INGREDIENTS:
    # Randomly select one item from each key and add to ingredients list
            ingredients.append(choice(INGREDIENTS[key]))

    ingredients = ','.join(ingredients)
    # Pass that list into EDAMAM API and save recipe results
    results = pass_ingredients_to_recipes(ingredients)
    recipes = save_recipes_and_ingredients_from_response(results)
    # Randomly select 5 results and add to a randomly selected user



def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


if __name__ == "__main__":
    init_app()
    db.create_all()
    load_food_type()
    load_fake_users()
    load_fake_ingredients()

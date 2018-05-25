"""Utility file to meal planning database."""

import datetime
from sqlalchemy import func
from faker import Faker

from model import (User, FoodType, Recipe, Ingredient, 
    RecipeIngredient, UserRecipe, Score, connect_to_db, db, init_app)
from mealplan_db import *


# Create alias for Faker()
fake = Faker()


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
    """ Add proteins to the ingredients table."""

    ingredients = {'Proteins': ['chicken', 'steak', 'tofu', 'eggs'],
                    'Produce': ['broccoli', 'carrots', 'mushrooms', 'spinach', 
                        'tomatoes'],
                    'Grains and Pasta': ['rice', 'quinoa', 'bread']}

    for key in ingredients:
        for ingredient in ingredients[key]:
            food_type = get_ingredient_type(key)
            create_ingredient(ingredient, food_type.type_id)


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

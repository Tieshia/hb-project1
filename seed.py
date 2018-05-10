"""Utility file to meal planning database."""

import datetime
from sqlalchemy import func

from model import (User, FoodType, Recipe, Ingredient, 
    StoredIngredient, CookedRecipe, Score, connect_to_db, db, init_app)

def load_food_type():
    """Load food type by list below."""

    food_groups = ['Dairy and Egg Products', 'Spices and Herbs', 'Fats and Oils',
        'Proteins', 'Soups, Sauces, and Gravies', 'Produce', 'Nuts and Seeds', 
        'Grains and Pasta', 'Miscellaneous', 'Unknown']

    for item in food_groups:
        food_group = FoodType(food_type=item)

        # Add group to the session or it won't ever be stored.
        db.session.add(food_group)

    # Once done, commit work.
    db.session.commit()

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

""" Meal Planning"""

import os
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, FoodType, Recipe, Ingredient, 
    StoredIngredient, CookedRecipe, Score)


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/login', methods=['GET'])
def login():
    """Get info from login page."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def verify_credentials():
    """Verifies user credentials"""
    pass

    # Takes in email and password
    # if email exists:
        # if password matches:
            # redirect to user profile and add user to session
        # else redirect and flash invalid
    # else redirect and flash invalid

@app.route('/register', methods=['GET'])
def register():
    """Get info from registration page."""

    return render_template("register.html")


@app.route('/register', methods=['POST'])
def add_new_user():
    """Add user to database."""
    pass

    # Take user info
    # If email already in system:
        # Flash invalid email and redirect to login
    # else create user and add to database
        # add user to session
        # redirect to initial profile setup

@app.route('/create-profile', methods=['GET'])
def create-profile():
    """ Initializes user preferences."""
    pass

    # render create profile template


@app.route('/create-profile', methods=['POST'])
def update_stored_ingredients():
    """ adds stored ingredients to database."""
    pass

    # get ingredients
    # create store_ingredients
    # add to database
    # flash successfully added and redirect to user-profile


@app.route('/user-profile')
def show_user_profile():
    """Renders profile information for specific user."""
    pass

    # get user from session
    # pull up stored_ingredients and pass into template
    # pull up active revipes on user_recipes and pass into template 
    # render profile template


@app.route('/add-ingredient', methods=['POST'])

@app.route('/recipe-made', methods=['POST'])


@app.route('/plan-meal', methods=['GET'])
def get_ingredients():
    """ Get user specified ingredients and show possible meals."""
    pass

    # return template for ingredient items; add meal preferences here as well?


@app.route('/plan-meal', methods=['POST'])
def show_meals():
    """ Pass ingredients into spoonacular API and show meal results."""
    pass

    # get ingredients from meal plan
    # pass into spoonacular api
    # pass results into meal plan template and render 


@app.route('/scores')
def show_score():
    """Show all scores for user in session."""
    pass

    # Get user from session and pass their scores into render template


@app.route('/score-recipe/<int: recipe_id>', methods=['GET'])
def get_score():
    """show form to have user update score."""
    pass

    # render template for scoring recipe


@app.route('/score-recipe/<int: recipe_id>', methods=['POST'])
def update_score():
    """Adds/updates user score for recipe."""
    pass

    # If user score for recipe already exists:
        # update in database
    # Else
        # Add new score row to database


################################################################################

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")

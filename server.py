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

    # Takes in email and password
    # if email exists:
        # if password matches:
            # redirect to user profile
        # else redirect and flash invalid
    # else redirect and flash invalid

@app.route('/register', methods=['GET'])
def register():
    """Get info from registration page."""

    return render_template("register.html")


@app.route('/register', methods=['POST'])
def add_new_user():
    """Add user to database."""

    # Take user info
    # If email already in system:
        # Flash invalid email and redirect to login
    # else create user and add to database
        # redirect to initial profile setup

@app.route('/create-profile', methods=['GET'])
def create-profile():
    """ Initializes user preferences."""

    # render create profile template


@app.route('/create-profile', methods=['POST'])
def update_stored_ingredients():
    """ adds stored ingredients to database."""

    # get ingredients
    # create store_ingredients
    # add to database
    # flash successfully added and redirect to user-profile


@app.route('/user-profile')
def show_user_profile():
    """Renders profile information for specific user."""

    # get user from session
    # pull up stored_ingredients and pass into template
    # render profile template


@app.route('/plan-meal', methods=['GET'])
def get_ingredients():
    """ Get user specified ingredients and show possible meals."""

    # return template for ingredient items; add meal preferences here as well?


@app.route('/plan-meal', methods=['POST'])
def show_meals():
    """ Pass ingredients into spoonacular API and show meal results."""

    # get ingredients from meal plan
    # pass into spoonacular api
    # pass results into meal plan template and render 





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

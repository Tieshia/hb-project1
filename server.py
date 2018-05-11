""" Meal Planning"""

import os
import requests
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, FoodType, Recipe, Ingredient, 
    StoredIngredient, UserRecipe, Score)


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
    # TEST DB -- DONE
    # Takes in email and password
    email = request.form.get('email')
    password = request.form.get('password')
    # if email exists:
    check_user = User.query.filter_by(email=email).first()

    if check_user:
        # if password matches:
        if check_user.password == password:
            # redirect to user profile and add user to session
            session['user'] = check_user.user_id
            flash('Welcome back!')
            return render_template('profile.html')
        # else redirect and flash invalid
        else:
            flash('Invalid credentials.')
            return redirect('/login')
    # else redirect and flash invalid
    else:
        flash('Invalid credentials')
        return redirect('/login')


@app.route('/register', methods=['GET'])
def register():
    """Get info from registration page."""

    return render_template("register.html")


@app.route('/register', methods=['POST'])
def add_new_user():
    """Add user to database."""

    # TEST DB

    # Take user info
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    # If email already in system:
    check_user = User.query.filter_by(email=email).first()

    if check_user:
        # Flash invalid email and redirect to login
        flash('Invalid credentials')
        return redirect('/register')
    # else create user and add to database
    else:
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        # add user to session
        session['user'] = new_user.user_id
        # redirect to initial profile setup
        return render_template('profile-setup.html')

@app.route('/create-profile', methods=['GET'])
def create_profile():
    """ Initializes user preferences."""
    pass

    # render create profile template


@app.route('/create-profile', methods=['POST'])
def update_stored_ingredients():
    """ adds stored ingredients to database."""
    pass

    # TEST DB

    # get ingredients
    # create store_ingredients
    # add to database
    # flash successfully added and redirect to user-profile


@app.route('/user-profile')
def show_user_profile():
    """Renders profile information for specific user."""
    pass

    # TEST DB

    # get user from session
    # pull up stored_ingredients and pass into template
    # pull up active revipes on user_recipes and pass into template 
    # render profile template


@app.route('/update-ingredients', methods=['POST'])
def update_ingredients():
    """ Update stored_ingredients."""
    pass

    # TEST DB

@app.route('/recipe-made', methods=['POST'])
def mark_recipe():
    """Change user_recipe to inactive and increment times_counted."""
    pass

    # TEST DB


@app.route('/plan-meal', methods=['GET'])
def get_ingredients():
    """ Get user specified ingredients and show possible meals."""
    pass

    # return template for ingredient items; add meal preferences here as well?


def get_recipes(params):
    """Get meal results from spoonacular."""

    # pass into EDAMAM api
    r = requests.get(requests.get("https://api.edamam.com/search", 
        params=payload))
    return r.json()


@app.route('/plan-meal', methods=['POST'])
def show_meals():
    """ Pass ingredients into edamam API and show meal results."""
    
    # get ingredients from meal plan
    ingredients = request.form.get("ingredients")
    ingredients = ','.join(ingredients)
    
    params = {"app_id": os.environ['EDAMAM_SECRET_ID'],
    "app_key": os.environ['EDAMAM_SECRET_KEY'],
    "ingredients": ingredients}
    r = get_recipes(params)

    return render_template('meal-plan.html', results=r)

@app.route('/check-meal', methods=['POST'])
def add_meal_to_plan():
    """Pass selected meals into UserRecipes."""

    # TEST DB


@app.route('/scores')
def show_score():
    """Show all scores for user in session."""
    pass

    # TEST DB

    # Get user from session and pass their scores into render template


@app.route('/score-recipe/<int:recipe_id>', methods=['GET'])
def get_score():
    """show form to have user update score."""
    pass

    # render template for scoring recipe


@app.route('/score-recipe/<int:recipe_id>', methods=['POST'])
def update_score():
    """Adds/updates user score for recipe."""
    pass

    # TEST DB 

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

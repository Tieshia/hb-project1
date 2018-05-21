""" Meal Planning"""

import os
import requests
import pdb
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from mealplan_db import (get_user, create_new_user, get_active_user_recipes,
    create_user_recipe, get_ingredient, get_ingredient_type, create_ingredient,
    add_ingredient, get_recipe_by_url, get_recipe_by_id, create_recipe, get_recipe_ingredient, 
    create_recipe_ingredient, mark_meal_made, get_score, upsert_score)

from model import connect_to_db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index(): # -- TESTED
    """Homepage."""

    return render_template("homepage.html")


@app.route('/login', methods=['GET'])
def login(): # -- TESTED
    """Get info from login page."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def verify_credentials():
    """Verifies user credentials"""
    # TEST DB -- DONE
    
    # If someone already logged in, redirect to user profile:
    if session['user']:
        flash('Already logged in!')
        return redirect('/user-profile')
    # Else varify credentials and log user in
    else:
        # Takes in email and password
        email = request.form.get('email')
        password = request.form.get('password')
        # if email exists:

        check_user = get_user(email) 

        if check_user:
            # if password matches:
            if check_user.password == password:
                # redirect to user profile and add user to session
                session['user'] = check_user.user_id
                flash('Welcome back!')
                return redirect('/user-profile')
            # else redirect and flash invalid
            else:
                flash('Invalid credentials.')
                return redirect('/login')
        # else redirect and flash invalid
        else:
            flash('Invalid credentials')
            return redirect('/login')


@app.route('/logout', methods=['POST'])
def log_user_out():
    """Logs user out and removes user from session."""
    
    # If no user in session, redirect to log in
    if session['user']:
        del session['user']
        flash('Goodbye!')
        return redirect('/')
    else:
        flash('No user logged in')
        return redirect('/')


@app.route('/register', methods=['GET'])
def register():
    """Get info from registration page."""

    return render_template("register.html")


@app.route('/register', methods=['POST'])
def add_new_user():
    """Add user to database."""

    # TEST DB -- TESTED

    # Take user info
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    # If email already in system:

    # WROTE DB FUNCTION FOR THIS
    check_user = get_user(email)

    if check_user:
        # Flash invalid email and redirect to login
        flash('Invalid credentials')
        return redirect('/login')
    # else create user and add to database
    else:
        new_user = create_new_user(name, email, password)
        # add user to session
        session['user'] = new_user.user_id
        # redirect to initial profile setup
        return render_template('profile-setup.html')


@app.route('/create-profile', methods=['GET'])
def create_profile(): # -- TESTED
    """ Initializes user preferences."""

    # render create profile template
    return render_template('profile-setup.html')


@app.route('/user-profile')
def show_user_profile():
    """Renders profile information for specific user."""

    # TEST DB -- TESTED

    # get user from session
    user_id = session['user']
    # pull up stored_ingredients and pass into template
    user_recipes = get_active_user_recipes(user_id)
    # pull up active recipes on user_recipes and pass into template 
    # render profile template
    return render_template('profile.html', recipes=user_recipes)


@app.route('/plan-meal', methods=['GET'])
def get_ingredients():
    """ Get user specified ingredients and show possible meals."""

    # return template for ingredient items
    return render_template('plan-meal.html')


def get_recipes(payload):
    """Get meal results from spoonacular."""

    # pass into EDAMAM api
    r = requests.get("https://api.edamam.com/search", 
        params=payload)
    data = r.json()    
    return data['hits']


@app.route('/plan-meal', methods=['POST'])
def show_meals():
    """ Pass ingredients into edamam API and show meal results."""
    
    # get ingredients from meal plan
    # get ingredients
    ingredients = request.form.getlist('ingredients')
    types = request.form.getlist('types')

    ingredient_rows = []

    # create store_ingredients
    for i in range(len(ingredients)):
        new_ingredient = add_ingredient(ingredients[i], types[i])

        ingredient_rows.append(new_ingredient)

    # format ingredients to pass into EDAMAM API
    ingredients = ','.join(ingredients)
    
    params = {"app_id": os.environ['EDAMAM_SECRET_ID'],
    "app_key": os.environ['EDAMAM_SECRET_KEY'],
    "q": ingredients}
    results = get_recipes(params)

    recipes=[]

    for recipe in results:
        # If recipe url currently not in Recipes
        recipe_result = get_recipe(recipe['recipe']['url'])
        if recipe_result is None:
            # Create new recipe and add to Recipes
            create_recipe(recipe['recipe']['label'], recipe['recipe']['url'], 
                recipe['recipe']['image'])
        else:
            pass
        recipes.append(get_recipe(recipe['recipe']['url']))

    # if recipe_id not in Recipe_ingredients:
    for recipe in recipes:
        recipe_ingredient = get_recipe_ingredient(recipe.recipe_id)
        if recipe_ingredient is None:
            # Add to recipe_ingredients and commit
            for ingredient in ingredient_rows:
                create_recipe_ingredient(recipe.recipe_id, ingredient.ingredient_id)
        else:
            pass

    return render_template('meal-plan.html', results=recipes)


@app.route('/check-meal', methods=['POST'])
def add_meal_to_plan():
    """Pass selected meals into UserRecipes."""

    selected_recipes = request.form.getlist('recipes')

    for recipe_id in selected_recipes:
        recipe_id = int(recipe_id)
        
        create_user_recipe(recipe_id, session['user'])

    flash('Successfully added!')
    return redirect('/user-profile')


@app.route('/made-meal', methods=['POST'])
def update_user_meal():
    """Update user meal once made."""

    # Get recipe id from request.form
    recipe_id = request.form.get('recipe_id')
    # recipe_id = int(recipe_id)
    # Add recipe id to session to carry over into score-recipe redirect
    session['recipe_id'] = recipe_id

    # Update user recipe to inactive and increment times_cooked by 1
    mark_meal_made(recipe_id, session['user'])

    # Flash 'Logged.' and redirect to user profile
    flash('Logged.')
    # **Change to score-recipe route
    return redirect('/score-recipe')


@app.route('/score-recipe', methods=['GET'])
def get_user_score():
    """Renders template for collecting user info."""
    
    return render_template('score-recipe.html')


@app.route('/score-recipe', methods=['POST'])
def update_score():
    """Adds/updates user score for recipe."""

    # TEST DB -- TESTED

    # Get score from request.form
    score = request.form.get('score')

    upsert_score(session['recipe_id'], session['user_id'], score)

    del session['recipe_id']

    # redirect to user profile
    flash('Successfully updated')
    return redirect('/user-profile')


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

""" Meal Planning"""

import os
import requests
import pdb
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from mealplan_db import *
from model import connect_to_db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


######################### INDEX ################################################

@app.route('/')
def index(): # -- TESTED
    """Homepage."""

    if session.get('user'):
        flash('Already logged in!')
        return redirect('/user-profile')
    else:
        return render_template("homepage.html")


############################# LOGGING IN/OUT ###################################

@app.route('/login', methods=['GET'])
def login(): # -- TESTED
    """Get info from login page."""
    
    if session.get('user'):
        flash('Already logged in!')
        return redirect('/user-profile') # -- TESTED
    else:
        return render_template("login.html") # -- TESTED


@app.route('/login', methods=['POST'])
def verify_credentials(): # -- TESTED
    """Verifies user credentials"""
    
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
            return redirect('/user-profile') # -- TESTED
        # else redirect and flash invalid
        else:
            flash('Invalid credentials.') 
            return redirect('/login') # -- TESTED
    # else redirect and flash invalid
    else:
        flash('Invalid credentials')
        return redirect('/login') # -- TESTED


@app.route('/logout', methods=['POST'])
def log_user_out(): # -- TESTED
    """Logs user out and removes user from session."""
    
    # If no user in session, redirect to log in
    if session.get('user'):
        del session['user']
        flash('Goodbye!')
        return redirect('/') # -- TESTED
    else:
        flash('No user logged in.')
        return redirect('/') # -- TESTED


##################### REGISTERING ##############################################

@app.route('/register', methods=['GET'])
def register(): # -- TESTED
    """Get info from registration page."""
    if session.get('user'):
        flash('User already logged in')
        return redirect('/user-profile') # -- TESTED
    else:
        return render_template("register.html") # -- TESTED


@app.route('/register', methods=['POST'])
def add_new_user(): # -- TESTED
    """Add user to database."""

    # Take user info
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    # If email already in system:

    check_user = get_user(email)
    if check_user:
        # Flash invalid email and redirect to login
        flash('Invalid credentials') # -- TESTED
        return redirect('/login')
    # else create user and add to database
    else:
        new_user = create_new_user(name, email, password)
        # add user to session
        session['user'] = new_user.user_id
        # redirect to initial profile setup
        return redirect('/user-profile') # -- TESTED


###################### SHOW USER PROFILE ######################################

@app.route('/user-profile')
def show_user_profile(): # -- TESTED
    """Renders profile information for specific user."""

    # get user from session
    user_id = session['user']
    # pull up stored_ingredients and pass into template
    user_recipes = get_active_user_recipes(user_id)
    # pull up active recipes on user_recipes and pass into template 
    # render profile template
    # if not user_recipes:
    #     user_recipes = None
    return render_template('profile.html', recipes=user_recipes) # -- TESTED


######################## GET MEAL PLAN ########################################

@app.route('/plan-meal', methods=['GET'])
def get_ingredients(): # -- TESTED
    """ Get user specified ingredients and show possible meals."""

    # return template for ingredient items
    return render_template('plan-meal.html')


def get_recipes(payload): # -- TESTED
    """Get meal results from spoonacular."""

    # pass into EDAMAM api
    r = requests.get("https://api.edamam.com/search", 
        params=payload)
    data = r.json()    
    return data['hits']


@app.route('/plan-meal', methods=['POST'])
def show_meals(): # -- TESTED
    """ Pass ingredients into edamam API and show meal results."""
    
    # get ingredients from meal plan
    # get ingredients
    ingredients = request.form.getlist('ingredients')
    types = request.form.getlist('types')

    ingredient_rows = []

    # create ingredient
    for i in range(len(ingredients)):
        new_ingredient = add_ingredient(ingredients[i], types[i])
        ingredient_rows.append(new_ingredient)
    # format ingredients to pass into EDAMAM API
    ingredients = ','.join(ingredients)
    
    params = {"app_id": os.environ['EDAMAM_SECRET_ID'],
    "app_key": os.environ['EDAMAM_SECRET_KEY'],
    "q": ingredients}
    results = get_recipes(params)

    recipes=set()

    for recipe in results:
        # If recipe url currently not in Recipes
        add_json_response_to_recipes(recipe['recipe']['label'], 
            recipe['recipe']['url'], recipe['recipe']['image'])
        recipes.add(get_recipe_by_url(recipe['recipe']['url']))

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


@app.route('/check-meal', methods=['POST']) # -- TESTED
def add_meal_to_plan():
    """Pass selected meals into UserRecipes."""

    selected_recipes = request.form.getlist('recipes')

    for recipe_id in selected_recipes:
        recipe_id = int(recipe_id)
        
        create_user_recipe(recipe_id, session['user'])

    flash('Successfully added!')
    return redirect('/user-profile')



###################### TRACK MEAL MADE AND SCORE ###############################

@app.route('/made-meal', methods=['POST'])
def update_user_meal(): # -- TESTED
    """Update user meal once made."""

    # Get recipe id from request.form
    recipe_id = request.form.get('recipe_id')
    # recipe_id = int(recipe_id)
    # Add recipe id to session to carry over into score-recipe redirect
    session['recipe_id'] = recipe_id

    # Update user recipe to inactive and increment times_cooked by 1
    mark_meal_made(recipe_id, session['user'])

    # Flash 'Logged.' and redirect to score-recipe
    flash('Logged, please score your recipe.')
    # **Change to score-recipe route
    return redirect('/score-recipe')


@app.route('/score-recipe', methods=['GET'])
def get_user_score(): # -- TESTED
    """Renders template for collecting user info."""
    
    return render_template('score-recipe.html')


@app.route('/score-recipe', methods=['POST'])
def update_score():
    """Adds/updates user score for recipe."""

    # Get score from request.form
    score = request.form.get('score')

    upsert_score(session['recipe_id'], session['user'], score)

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

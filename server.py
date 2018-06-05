""" Meal Planning"""

import os
import requests
from random import choice, sample
import pdb
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from mealplan_db import *
from mealplan_recipes import *
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
    print "email:", email
    print "pw:", password
    # if email exists:

    check_user = get_user(email) 
    print "retrieved user"

    if check_user:
        # if password matches:
        if check_user.password == password:
            # redirect to user profile and add user to session
            session['user'] = check_user.user_id
            flash('Welcome back!')
            print "valid user and redirecting"
            return redirect('/user-profile') # -- TESTED
        # else redirect and flash invalid
        else:
            flash('Invalid credentials.') 
            print "invalid creds, pw wrong"
            return redirect('/login') # -- TESTED
    # else redirect and flash invalid
    else:
        flash('Invalid credentials')
        print "invalid user"
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
    # pull up highest rated recipes and pass into template
    highest_random_recipes = get_random_highest_rated_recipes()
    # pull up active recipes on user_recipes and pass into template 
    user_recipes = get_active_user_recipes(user_id)
    # render profile template
    # if not user_recipes:
    #     user_recipes = None
    return render_template('profile.html', highest=highest_random_recipes,
        recipes=user_recipes) # -- ** REQUIRES NEW TESTING **


######################## GET MEAL PLAN ########################################


@app.route('/plan-meal', methods=['POST'])
def show_meals(): # -- TESTED
    """ Pass ingredients into edamam API and show meal results."""
    
    # get ingredients from meal plan form
    ingredients = request.form.getlist('ingredients')
    types = request.form.getlist('types')

    meal_plan_recipes_sample = get_random_sampling_of_diverse_recipes(ingredients, 
                                                                        types)

    return render_template('meal-plan.html', results=meal_plan_recipes_sample)


@app.route('/check-meal', methods=['POST']) # -- TESTED
def add_meal_to_plan():
    """Pass selected meals into UserRecipes."""

    selected_recipes = request.form.getlist('recipes')
    if selected_recipes:
        for recipe_id in selected_recipes:
            recipe_id = int(recipe_id)
            
            create_user_recipe(recipe_id, session['user'])

    flash('Successfully added!')
    return redirect('/user-profile')



###################### TRACK MEAL MADE AND SCORE ###############################


# Troubleshoot with print statements for JS and python
@app.route('/made-and-scored-meal', methods=['POST'])
def update_user_meal(): # -- TESTED
    """Update user meal once made."""

    # Get recipe id from request.form
    recipe_id = request.form.get('recipe_id')
    # Get score from request.form
    score = request.form.get('score')

    upsert_score(int(recipe_id), session['user'], int(score))

    # Update user recipe to inactive and increment times_cooked by 1
    mark_meal_made(int(recipe_id), session['user'])

    # Return success dict and on js side have callback to execute DOM changes 
    return "Success"

######################### RECIPE PAGES #########################################

@app.route('/all-recipes')
def show_all_recipes():
    """Render template with all recipes in database."""

    all_recipes = get_all_recipes()
    return render_template('all-recipes.html', recipes=all_recipes)


@app.route('/user-profile/recipes')
def show_user_recipes():
    """Render template with all user recipes and scores in database."""

    user_recipes = get_user_scores(session['user'])
    return render_template('user-recipes.html', recipes=user_recipes)


############################# CLEAR MEALS ######################################


@app.route('/clear-meals', methods=['POST'])
# CURRENTLY CLEARING ALL BUT ONE??
def clear_meals():
    """Mark all active meals as inactive."""
    clear_recipes(session['user'])
    # FIGURE OUT WAY TO DO THIS WITH AN AJAX CALL
    return redirect('/user-profile')


######################## AJAX TESTING ROUTES ###################################
@app.route('/test', methods=['POST'])
def test_rating_alert_with_ajax():
    """Test to see if star rating can be passed via AJAX."""

    score = request.form.get('score')

    return "You rated the recipe {}".format(score)


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

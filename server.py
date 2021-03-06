""" Meal-of-Fortune meal planning application.
    Copyright (C) 2018  Tieshia Francis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    For further information, please contact: francistie@gmail.com
    License available at LICENSE.txt.
"""

import os
import requests
from random import choice, sample
from jinja2 import StrictUndefined
import bcrypt

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from mealplan_db import (get_user, create_new_user,
                         get_random_highest_rated_recipes, get_active_user_recipes, create_user_recipe,
                         upsert_score, mark_meal_made, get_all_recipes, get_user_scores, delete_user_recipe, 
                         clear_recipes)
from mealplan_recipes import get_random_sampling_of_diverse_recipes
from model import connect_to_db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


######################### INDEX ################################################


@app.route('/')
def index():  # -- TESTED
    """Homepage."""

    if session.get('user'):
        flash('Already logged in!')
        return redirect('/user-profile')
    else:
        return render_template("homepage.html")


############################# LOGGING IN/OUT ###################################


@app.route('/login', methods=['GET'])
def render_login_template():  # -- TESTED
    """Get info from login page."""

    if session.get('user'):
        flash('Already logged in!')
        return redirect('/user-profile')  # -- TESTED
    else:
        return render_template("login.html")  # -- TESTED


@app.route('/login', methods=['POST'])
def verify_credentials_and_redirect_to_user_profile():  # -- TESTED
    """Verifies user credentials"""

    # Takes in email and password
    email = request.form.get('email')
    password = request.form.get('password')
    # if email exists:

    check_user = get_user(email)  # -- mealplan_db.py

    if check_user:
        # if password matches:
        # *** Get familiar with bcrypt checkpw and encode methods
        is_password_match = bcrypt.checkpw(password.encode('utf-8'),
                                           check_user.password.encode('utf-8'))
        if is_password_match:
            # redirect to user profile and add user to session
            session['user'] = check_user.user_id
            flash('Welcome back!')
            return redirect('/user-profile')  # -- TESTED
        # else redirect and flash invalid
        else:
            flash('Invalid credentials.')
            return redirect('/login')  # -- TESTED
    # else redirect and flash invalid
    else:
        flash('Invalid credentials')
        return redirect('/login')  # -- TESTED


@app.route('/logout', methods=['POST'])
def remove_user_from_session():  # -- TESTED
    """Logs user out and removes user from session."""

    # If no user in session, redirect to log in
    if session.get('user'):
        del session['user']
        flash('Goodbye!')
        return redirect('/')  # -- TESTED
    else:
        flash('No user logged in.')
        return redirect('/')  # -- TESTED


##################### REGISTERING ##############################################

@app.route('/register', methods=['GET'])
def render_register_template():  # -- TESTED
    """Get info from registration page."""
    if session.get('user'):
        flash('User already logged in')
        return redirect('/user-profile')  # -- TESTED
    else:
        return render_template("register.html")  # -- TESTED


@app.route('/register', methods=['POST'])
def add_new_user_and_redirect_to_user_profile():  # -- TESTED
    """Add user to database."""

    # Take user info
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    # If email already in system:

    check_user = get_user(email)  # -- mealplan_db.py
    if check_user:
        # Flash invalid email and redirect to login
        flash('Invalid credentials')  # -- TESTED
        return redirect('/login')
    # else create user and add to database
    else:
        # ** Get familiar with bcrypt hashpw and gensalt methods
        # Create hash of password before it is stored in database
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'),
                                  bcrypt.gensalt())
        new_user = create_new_user(name, email, hashed_pw)  # -- mealplan_db.py
        # add user to session
        session['user'] = new_user.user_id
        # redirect to initial profile setup
        return redirect('/user-profile')  # -- TESTED


###################### SHOW USER PROFILE ######################################

@app.route('/user-profile')
def render_user_profile_template():  # -- TESTED
    """Renders profile information for specific user."""

    # get user from session
    user_id = session['user']
    # pull up highest rated recipes and pass into template
    highest_random_recipes = get_random_highest_rated_recipes()  # mealplan_db.py
    # pull up active recipes on user_recipes and pass into template
    user_recipes = get_active_user_recipes(user_id)  # mealplan_db.py
    # render profile template
    # if not user_recipes:
    #     user_recipes = None
    return render_template('profile.html', highest=highest_random_recipes,
                           recipes=user_recipes)


######################## GET MEAL PLAN ########################################


@app.route('/plan-meal', methods=['POST'])
def show_recipes_from_EDAMAM_response():  # -- TESTED
    """ Pass ingredients into edamam API and show meal results."""

    # get ingredients from meal plan form
    ingredients = request.form.getlist('ingredients')
    types = request.form.getlist('types')

    meal_plan_recipes_sample = get_random_sampling_of_diverse_recipes(ingredients,
                                                                      types)
    # -- mealplan_recipes.py

    return render_template('meal-plan.html', results=meal_plan_recipes_sample)


@app.route('/check-meal', methods=['POST'])  # -- TESTED
def add_recipe_to_plan():
    """Pass selected meals into UserRecipes."""

    selected_recipes = request.form.getlist('recipes')
    print "Selected recipe ids:", selected_recipes
    if selected_recipes:
        for recipe_id in selected_recipes:
            recipe_id = int(recipe_id)

            create_user_recipe(recipe_id, session['user'])  # -- mealplan_db.py

    flash('Successfully added!')
    return redirect('/user-profile')


###################### TRACK MEAL MADE AND SCORE ###############################


# Troubleshoot with print statements for JS and python
@app.route('/made-and-scored-meal', methods=['POST'])
def mark_user_meal_as_made_and_update_score():  # -- TESTED
    """Update user meal once made."""

    # Get recipe id from request.form
    recipe_id = request.form.get('recipe_id')
    # Get score from request.form
    score = request.form.get('score')

    # -- mealplan_db.py
    upsert_score(int(recipe_id), session['user'], int(score))

    # Update user recipe to inactive and increment times_cooked by 1
    mark_meal_made(int(recipe_id), session['user'])  # -- mealplan_db.py

    # Return success dict and on js side have callback to execute DOM changes
    return "Success"

######################### RECIPE PAGES #########################################


@app.route('/all-recipes')
def show_all_recipes():
    """Render template with all recipes in database."""

    all_recipes = get_all_recipes()  # -- mealplan_db.py
    return render_template('all-recipes.html', recipes=all_recipes)


@app.route('/user-profile/recipes')
def show_user_recipes():
    """Render template with all user recipes and scores in database."""

    user_recipes = get_user_scores(session['user'])  # -- mealplan_db.py
    return render_template('user-recipes.html', recipes=user_recipes)


############################# CLEAR MEAL(S) ####################################


@app.route('/clear-meals', methods=['POST'])
def clear_meals():
    """Mark all active meals as inactive."""
    clear_recipes(session['user'])  # -- mealplan_db.py
    # ** FIGURE OUT WAY TO DO THIS WITH AN AJAX CALL
    return redirect('/user-profile')


@app.route('/delete-recipe', methods=['POST'])
def delete_selected_recipe():
    """Delete user_recipe specified by user."""

    # **YOUR ARE HERE**; SAYING TAKES 0 ARGUMENTS FOR SOME REASON
    recipe_id = request.form.get('recipe_id')
    delete_user_recipe(session['user'], int(recipe_id))  # -- mealplan_db.py
    # flash('Successfully deleted!')
    # return redirect('/user-profile')
    return ("Successfully deleted recipe!")


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
    app.debug = False

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")

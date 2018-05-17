""" Meal Planning"""

import os
import requests
import pdb
from datetime import datetime
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
    
    del session['user']
    flash('Goodbye!')
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
def create_profile(): # -- TESTED
    """ Initializes user preferences."""

    # render create profile template
    return render_template('profile-setup.html')


@app.route('/create-profile', methods=['POST'])
def update_stored_ingredients():
    """ adds stored ingredients to database."""

    # TEST DB -- TESTED

    # get ingredients
    ingredients = request.form.get('ingredients')
    ingredients = ingredients.split(',')
    types = request.form.get('types')
    types = types.split(',')

    # create store_ingredients
    for i in range(len(ingredients)):
        # If not in ingredients, add to ingredients:
        if Ingredient.query.filter_by(ingredient_name=(ingredients[i])).first() is None:
            ing_type = FoodType.query.filter_by(food_type=(types[i])).first()
            new_ingredient = Ingredient(ingredient_name=(ingredients[i]), type_id=ing_type.type_id)
            db.session.add(new_ingredient)
        #else add to database
        else:
            pass
        user_ingredient = Ingredient.query.filter_by(ingredient_name=(ingredients[i])).first()
        user_ingredient_id = user_ingredient.ingredient_id
        new_user_ingredient = StoredIngredient(ingredient_id=user_ingredient_id, 
                                                user_id=session['user'],
                                                added_at=datetime.now())
        db.session.add(new_user_ingredient)

    db.session.commit()
        

    # flash successfully added and redirect to user-profile
    flash('Successfully added!')
    return redirect('/user-profile')


@app.route('/user-profile')
def show_user_profile():
    """Renders profile information for specific user."""

    # TEST DB -- TESTED

    # get user from session
    user_id = session['user']
    # pull up stored_ingredients and pass into template
    user_ingredients = StoredIngredient.query.filter_by(user_id=user_id).all()
    user_recipes = UserRecipe.query.filter_by(active=True).all()
    # pull up active recipes on user_recipes and pass into template 
    # render profile template
    return render_template('profile.html', ingredients=user_ingredients,
            recipes=user_recipes)


@app.route('/add-ingredients', methods=['POST'])
def add_ingredients():
    """ Add stored_ingredients."""

    # TEST DB -- TESTED

    ingredients = request.form.get('ingredients')
    ingredients = ingredients.split(',')
    types = request.form.get('types')
    types = types.split(',')

    for i in range(len(ingredients)):
        if Ingredient.query.filter_by(ingredient_name=ingredients[i]).first() is None:
            food_type = FoodType.query.filter_by(food_type=types[i]).one()
            new_ingredient = Ingredient(ingredient_name=ingredients[i], 
                type_id=food_type.type_id)
            db.session.add(new_ingredient)
            db.session.commit()
        else:
            new_ingredient = Ingredient.query.filter_by(ingredient_name=ingredients[i]).first()
        new_user_ingredient = StoredIngredient(ingredient_id=new_ingredient.ingredient_id,
                            user_id=session['user'],
                            added_at=datetime.now())
        db.session.add(new_user_ingredient)
        db.session.commit()

    flash('Successfully added!')
    return redirect('/user-profile')


@app.route('/remove-ingredients', methods=['POST'])
def remove_ingredient():
    """Remove Stored Ingredient for user."""

    # TEST DB -- TESTED

    ingredients = request.form.get('ingredients')
    ingredients = ingredients.split(',')

    for i in range(len(ingredients)):
        main_ingredient = Ingredient.query.filter_by(ingredient_name=ingredients[i]).first()

        if main_ingredient:
            del_ingredient = StoredIngredient.query.filter_by(ingredient_id=main_ingredient.ingredient_id).first()
            if del_ingredient:
                db.session.delete(del_ingredient)
                db.session.commit()
            else:
                pass
        else:
            pass
    flash('Successfully deleted!')
    return redirect('/user-profile')


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
    ingredients = request.form.get("ingredients")
    # ingredients = ','.join(ingredients)
    
    params = {"app_id": os.environ['EDAMAM_SECRET_ID'],
    "app_key": os.environ['EDAMAM_SECRET_KEY'],
    "q": ingredients}
    results = get_recipes(params)

    recipes=[]

    for recipe in results:
        # If recipe url currently not in Recipes
        if Recipe.query.filter_by(url=recipe['recipe']['url']).first() is None:
            # Create new recipe and add to Recipes
            response_recipe = Recipe(recipe_name=recipe['recipe']['label'], 
                        url=recipe['recipe']['url'], 
                        image_url=recipe['recipe']['image'])
            db.session.add(response_recipe)
        else:
            response_recipe = Recipe.query.filter_by(url=recipe['recipe']['url']).first() 
        recipes.append(response_recipe)
    db.session.commit()

    return render_template('meal-plan.html', results=recipes)


@app.route('/check-meal', methods=['POST'])
def add_meal_to_plan():
    """Pass selected meals into UserRecipes."""

    # TEST DB -- TESTED :D

    selected_recipes = request.form.getlist('recipes')

    for recipe_id in selected_recipes:
        recipe_id = int(recipe_id)
        plan_recipe = UserRecipe.query.filter_by(recipe_id=recipe_id).first()
        if plan_recipe:
            plan_recipe.active = True
        else:
            new_user_recipe = UserRecipe(recipe_id=recipe_id, times_cooked=0, 
                active=True, user_id=session['user'])
            db.session.add(new_user_recipe)
    db.session.commit()

    flash('Successfully added!')
    return redirect('/user-profile')


@app.route('/made-meal', methods=['POST'])
def update_user_meal():
    """Update user meal once made."""

    # TEST DB -- TESTED 

    # Get recipe id from request.form
    recipe_id = request.form.get('recipe_id')
    recipe_id = int(recipe_id)

    # Update user recipe to inactive and increment times_cooked by 1
    user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe_id) &
        (UserRecipe.user_id == session['user'])).first()

    if user_recipe:
        user_recipe.active = False
        user_recipe.times_cooked = user_recipe.times_cooked + 1

        db.session.commit()

        # Add recipe id to session to carry over into score-recipe redirect
        session['recipe_id'] = recipe_id

        # **Flash 'Logged.' and redirect to user profile
        flash('Logged.')
        # **Change to score-recipe route
        return redirect('/score-recipe')
    else:
        pass


@app.route('/score-recipe', methods=['GET'])
def get_user_score():
    """Renders template for collecting user info."""
    
    return render_template('score-recipe.html')


@app.route('/score-recipe', methods=['POST'])
def update_score():
    """Adds/updates user score for recipe."""

    # TEST DB -- TESTED

    # Get scores from request.form
    effort = request.form.get('effort')
    taste = request.form.get('taste')
    # If user score for recipe already exists:
    user_score = Score.query.filter((Score.recipe_id == session['recipe_id']) & 
        (Score.user_id == session['user'])).first()

    if user_score:
        # update in database
        user_score.effort_score = effort
        user_score.taste_score = taste
        user_score.rated_at = datetime.now()
    # Else
    else:
        # Add new score row to database
        new_score = Score(rated_at=datetime.now(), effort_score=int(effort), taste_score=int(taste),
                    user_id=session['user'], recipe_id=session['recipe_id'])
        db.session.add(new_score)
    db.session.commit()

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

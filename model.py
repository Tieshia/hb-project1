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
"""Models and functions for creating database for Meal Planning project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of meal planning website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        """String representation of user object."""

        return "<id={} name={} email={}>".format(self.user_id,
                                                 self.name, self.email)


class FoodType(db.Model):
    """ Food group ingredient belongs in."""

    __tablename__ = "food_types"

    type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    food_type = db.Column(db.String(64))

    def __repr__(self):
        """String representation of food type object."""

        return "<id={} type={}>".format(self.type_id, self.food_type)


class Recipe(db.Model):
    """Recipe type."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_name = db.Column(db.String())
    url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        """String representation of recipe."""

        return "<id={} recipe={} url={}>".format(self.recipe_id,
                                                 self. recipe_name, self. url)


class Ingredient(db.Model):
    """Ingredients."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient_name = db.Column(db.String(64))
    type_id = db.Column(db.Integer, db.ForeignKey('food_types.type_id'))

    def __repr__(self):
        """String representation of ingredient."""

        return "<id={} ingredient={} type_id={}>".format(self.ingredient_id,
                                                         self.ingredient_name, self.type_id)


class RecipeIngredient(db.Model):
    """Recipes with each ingredient listed by user."""

    __tablename__ = "user_ingredients"

    user_ingredient_id = db.Column(db.Integer, autoincrement=True,
                                   primary_key=True)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))

    ingredients = db.relationship('Ingredient', backref='user_ingredients')
    recipes = db.relationship('Recipe', backref='user_ingredients')

    def __repr__(self):
        """String representation of user ingredient."""

        return "<id={} ingredient_id={} recipe_id={}>".format(self.user_ingredient_id,
                                                              self.ingredient_id, self.recipe_id)


class UserRecipe(db.Model):
    """Log of recipes cooked."""

    __tablename__ = "user_recipes"

    ur_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    times_cooked = db.Column(db.Integer)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    active = db.Column(db.Boolean)

    recipe = db.relationship('Recipe', backref='user_recipes')

    def __repr__(self):
        """String representation of a recipes cooked."""

        return "<id={} times_cooked={} recipe_id={} user_id={} active={}>".format(self.ur_id,
                                                                                  self.times_cooked, self.recipe_id, self.user_id, self.active)


class Score(db.Model):
    """User scores for recipes."""

    __tablename__ = "scores"

    score_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    rated_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))

    recipe = db.relationship('Recipe', backref='scores')

    def __repr__(self):
        """String representation of user score."""

        return "<id={} rated_at={} score={} recipe_id={}>".format(
            self.score_id, self.rated_at, self.score, self.recipe_id)


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data.
    Score.query.delete()
    UserRecipe.query.delete()
    RecipeIngredient.query.delete()
    Ingredient.query.delete()
    Recipe.query.delete()
    FoodType.query.delete()
    User.query.delete()
    password = 'test'
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'),
                                  bcrypt.gensalt())

    # Add sample data
    # Users
    tieshia = User(name="Tieshia", email="francistie@gmail.com",
                   password=hashed_pw)
    jane = User(name="Jane", email="jhacks@gmail.com", password=hashed_pw)

    # Food Type
    protein = FoodType(food_type='Proteins')
    produce = FoodType(food_type='Produce')

    db.session.add_all([tieshia, jane, protein, produce])
    db.session.commit()

    # Recipe
    recipe1 = Recipe(
        url='test1.com', image_url='test1_image.com', recipe_name='recipe1')
    recipe2 = Recipe(
        url='test2.com', image_url='test2_image.com', recipe_name='recipe2')
    recipe3 = Recipe(
        url='test3.com', image_url='test3_image.com', recipe_name='recipe3')

    # Ingredient
    steak = Ingredient(type_id=protein.type_id, ingredient_name='steak')
    broccoli = Ingredient(type_id=produce.type_id, ingredient_name='broccoli')

    db.session.add_all([recipe1, recipe2, recipe3, steak, broccoli])
    db.session.commit()

    # RecipeIngredient
    rec_ing1 = RecipeIngredient(ingredient_id=steak.ingredient_id,
                                recipe_id=recipe1.recipe_id)

    # User Recipes
    user_rec1 = UserRecipe(user_id=jane.user_id, times_cooked=0,
                           recipe_id=recipe1.recipe_id, active=False)
    user_rec2 = UserRecipe(user_id=jane.user_id, times_cooked=0,
                           recipe_id=recipe2.recipe_id, active=True)

    # Score
    user_score1 = Score(recipe_id=recipe1.recipe_id, score=5,
                        user_id=jane.user_id, rated_at=datetime.now())

    db.session.add_all([rec_ing1, user_rec1, user_rec2, user_score1])
    db.session.commit()


##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app, db_uri="postgresql:///mealplan"):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


###############################################################################
if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # from server import app
    # connect_to_db(app)
    # print "Connected to DB."

    init_app()

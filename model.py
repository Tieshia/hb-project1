"""Models and database functions for Meal Planning project."""

from flask_sqlalchemy import SQLAlchemy

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

        return "<id={} name={} email={}>".format( self.user_id,
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
    recipe_name = db.Column(db.String(64))
    url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        """String representation of recipe."""

        return "<id={} recipe={} url={}>".format(self.recipe_id,
            self. recipe_name, self. url)


class Ingredient(db.Model):
    """Ingredients for recipes."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient_name = db.Column(db.String(64))
    type_id = db.Column(db.Integer, db.ForeignKey('food_types.type_id'))

    food_types = db.relationship('FoodType', backref='ingredients')

    def __repr__(self):
        """String representation of ingrdient."""

        return "<id={} ingredient={} type_id={}>".format(self.ingredient_id,
            self.ingredient_name, self.type_id)


class StoredIngredient(db.Model):
    """Shows ingredients for each user."""

    __tablename__ = "stored_ingredients"

    record_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    added_at = db.Column(db.DateTime)

    ingredients = db.relationship('Ingredient', backref='stored_ingredients')
    users = db.relationship('User', backref='stored_ingredients')

    def __repr__(self):
        """String representation of a stored ingredient."""

        return "<id={} user_id={} added_at={}".format(self.ingredient_id,
            self.user_id, self.added_at)


class CookedRecipe(db.Model):
    """Log of recipes cooked."""

    __tablename__ = "cooked_recipes"

    cooked_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    added_at = db.Column(db.DateTime)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    recipes = db.relationship('Recipe', backref='cooked_recipes')
    users = db.relationship('User', backref='cooked_recipes')

    def __repr__(self):
        """String representation of a recipes cooked."""

        return "<id={} added_at={} recipe_id={} user_id={}>".format(self.cooked_id,
            self.added_at, self.recipe_id, self.user_id)


class Score(db.Model):
    """User scores for recipes."""

    __tablename__ = "scores"

    score_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    rated_at = db.Column(db.DateTime)
    effort_score = db.Column(db.Integer)
    taste_score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))

    recipes = db.relationship('Recipe', backref='scores')


    def __repr__(self):
        """String representation of user score."""

        return "<id={} rated_at={} effort={} taste={} recipe_id={}>".format(
            self.score_id, self.rated_at, self.effort_score, self.taste_score,
            self.recipe_id)


##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mealplan'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    init_app()

    # from server import app
    # connect_to_db(app)
    # print "Connected to DB."

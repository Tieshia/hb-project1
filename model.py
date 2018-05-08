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

class FoodType(db.Model):
    """ Food group ingredient belongs in."""

    __tablename__ = "food_types"

    type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    food_type = db.Column(db.String(64))


class Recipe(db.Model):
    """Recipe type."""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_name = db.Column(db.String(64))
    url = db.Column(db.String(200), nullable=True)
    image_url = db.Column(db.String(200), nullable=True)


class Ingredient(db.Model):
    """Ingredients for recipes."""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient_name = db.Column(db.String(64))
    type_id = db.Column(db.Integer, db.ForeignKey('food_types.type_id'))

    food_type = db.relationship('FoodType', backref='ingredients')


class StoredIngredient(db.Model):
    """Shows ingredients for each user."""

    __tablename__ = "stored_ingredients"

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    added_at = db.Column(db.DateTime)

    ingredient = db.relationship('Ingredient', backref='stored_ingredients')
    user = db.relationship('User', backref='users')







##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

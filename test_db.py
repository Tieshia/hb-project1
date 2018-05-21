from unittest import TestCase
from model import (User, Ingredient, RecipeIngredient, Recipe, UserRecipe, Score,
    connect_to_db, db, example_data, example_data_update_meal)
from server import app
from seed import load_food_type
from flask import session
from mealplan_db import * 

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client.
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()


    def test_get_user(self):
        """Test ability to get a user object based off login email."""

        user = get_user('jhacks@gmail.com')
        self.assertIsNotNone(user)


    def test_create_new_user(self):
        """Test abiility to add new user to database."""

        new_user = create_new_user('Sarah', 'sdevelops@gmail.com', 'test')
        self.assertIsNotNone(get_user('sdevelops@gmail.com'))


    def test_get_active_user_recipes(self):
        """Test retrieval of active user recipes based on user id."""

        user = get_user('jhacks@gmail.com')
        recipes = get_active_user_recipes(user.user_id)
        self.assertTrue(len(recipes) == 1) 


    def test_get_recipe_by_url(self):
        """Test retrieval of recipe based on url."""

        recipe = get_recipe_by_url('test3.com')
        self.assertIsNotNone(recipe)

    
    def test_get_recipe_by_id(self):
        """Test retrieval of recipe based on id."""

        recipe = get_recipe_by_url('test3.com')
        recipe_by_id = get_recipe_by_id(recipe.recipe_id)
        self.assertIsNotNone(recipe_by_id)


    def test_create_recipe(self):
        """Test addition of new recipe to database."""

        create_recipe('test6', 'test6.com', 'test6_image.com')
        test_recipe = get_recipe_by_url('test6.com')
        self.assertIsNotNone(test_recipe)


    def test_create_user_recipe(self):
        """Test addition of new user recipe to database."""

        recipe = get_recipe_by_url('test3.com')
        user = get_user('jhacks@gmail.com')
        create_user_recipe(recipe.recipe_id, user.user_id)
        user_recipe = UserRecipe.query.filter_by(recipe_id=recipe.recipe_id).first()
        self.assertIsNotNone(user_recipe)


    def test_get_ingredient(self):
        """Test retrieval of ingredient based on ingredient name."""

        ingredient = get_ingredient('steak')
        self.assertIsNotNone(ingredient)


    def test_get_ingredient_type(self):
        """Test retrieval of food type object based on ingreident type."""

        food_type = get_ingredient_type('Proteins')
        self.assertIsNotNone(food_type)


    def test_create_ingredient(self):
        """Test addition of new ingredient to database."""

        protein_ingredient = get_ingredient('steak')
        create_ingredient('chicken', protein_ingredient.type_id)
        new_ingredient = get_ingredient('chicken')
        self.assertIsNotNone(new_ingredient)


    def test_get_recipe_ingredient(self):
        """Test retrieval of recipe ingredient based on recipe id."""

        recipe = get_recipe_by_url('test1.com') 
        recipe_ingredient = get_recipe_ingredient(recipe.recipe_id)
        self.assertIsNotNone(recipe_ingredient)


    def test_create_recipe_ingredient(self):
        """Test addition of recipe ingredient to database."""

        recipe = get_recipe_by_url('test2.com')
        ingredient = get_ingredient('steak')
        create_recipe_ingredient(recipe.recipe_id, ingredient.ingredient_id)
        recipe_ingredient  = RecipeIngredient.query.filter((RecipeIngredient.recipe_id == recipe.recipe_id) &
            (RecipeIngredient.ingredient_id == ingredient.ingredient_id))
        self.assertIsNotNone(recipe_ingredient)





# class FlaskTestsDatabaseLoggedIn(TestCase):
#     """Flask database tests with user logged in to session."""

#     def setUp(self):
#         """Stuff to do before every test."""

#         # Get the Flask test client
#         self.client = app.test_client()
#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'key'
        
#         # Connect to test database
#         connect_to_db(app, "postgresql:///testdb")

#         # Create tables and add sample data
#         db.create_all()
#         example_data()

#         # Add user to Flask session
#         user = User.query.filter_by(name='Jane').first()
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user'] = user.user_id


#     def tearDown(self):
#         """Do at end of every test."""

#         db.session.close()
#         db.drop_all()

#     def test_check_meal(self):
#         """Test successfully adding items to meal plan."""

#         recipe3 = Recipe(url='test3.com', image_url='test3_image.com',
#                     recipe_name='recipe3')
#         recipe4 = Recipe(url='test4.com', image_url='test4_image.com',
#                     recipe_name='recipe4')
#         db.session.add_all([recipe3, recipe4])
#         db.session.commit()

#         recipe3_id = str(recipe3.recipe_id)
#         recipe4_id = str(recipe4.recipe_id)

#         result = self.client.post('/check-meal',
#                             data={'recipes': [recipe3_id, recipe4_id]},
#                             follow_redirects=True)

#         self.assertIn('Successfully added!', result.data)
#         self.assertIsNotNone(UserRecipe.query.filter_by(recipe_id=int(recipe3_id)).first())
#         self.assertIn('recipe3', result.data)
#         self.assertNotIn('No recipes to display', result.data)


#     def test_score_recipe(self):
#         """Test successfully adding/updating user score for recipe."""

#         # 
#         user = User.query.filter_by(name='Jane').first()
#         recipe = Recipe.query.filter_by(recipe_name='recipe1').first()
#         user_score = Score.query.filter((Score.recipe_id == recipe.recipe_id) & 
#             (Score.user_id == user.user_id))

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['recipe_id'] = recipe.recipe_id

#         result = self.client.post('/score-recipe',
#                             data={'effort': '1',
#                             'taste': '-1'},
#                             follow_redirects=True)

        
#         updated_score = Score.query.filter((Score.recipe_id == recipe.recipe_id) & 
#             (Score.user_id == user.user_id)).first()

#         self.assertTrue(updated_score.taste_score == -1)
#         self.assertIn('Successfully updated', result.data)


# class FlaskTestsDatabaseLoggedInCheckedMeal(TestCase):
#     """Flask database tests with user logged in to session."""

#     def setUp(self):
#         """Stuff to do before every test."""

#         # Get the Flask test client
#         self.client = app.test_client()
#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'key'
        
#         # Connect to test database
#         connect_to_db(app, "postgresql:///testdb")

#         # Create tables and add standard sample data
#         db.create_all()
#         example_data()

#         # Add user to Flask session
#         user = User.query.filter_by(name='Jane').first()
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user'] = user.user_id

#         # Add sample data for update_user_meal
#         example_data_update_meal()


#     def tearDown(self):
#         """Do at end of every test."""

#         db.session.close()
#         db.drop_all()

#     def test_update_user_meal(self):
#         """Test successfully updating UserRecipe once made."""

#         recipe = Recipe.query.filter_by(recipe_name='recipe3').first()
#         user_recipe = UserRecipe.query.filter_by(recipe_id=recipe.recipe_id).first()
#         user_recipe_id = user_recipe.recipe_id
#         user_recipe_id = str(user_recipe_id)

#         result = self.client.post('/made-meal',
#                             data={'recipe_id': user_recipe_id},
#                             follow_redirects=True)

#         used_recipe = UserRecipe.query.filter_by(recipe_id=int(user_recipe_id)).first()

#         self.assertTrue(used_recipe.times_cooked == 1)
#         self.assertFalse(used_recipe.times_cooked == 0)
#         self.assertFalse(used_recipe.active)
#         self.assertNotIn('recipe3', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()


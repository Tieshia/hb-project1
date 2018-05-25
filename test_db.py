from unittest import TestCase
from model import (User, Ingredient, RecipeIngredient, Recipe, UserRecipe, Score,
    connect_to_db, db, example_data)
from server import app
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
        # import pdb; pdb.set_trace()


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


    def test_add_json_response_to_recipes(self):
        """Test addition of json response recipe to database."""

        add_json_response_to_recipes('test7', 'test7.com', 'test7_image.com')
        test_recipe = get_recipe_by_url('test7.com')
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


    def test_add_ingredient(self):
        """Test addition of new ingredient to database based of type and name."""

        new_ingredient = add_ingredient('chicken', 'Proteins')
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


    def test_mark_meal_made(self):
        """Test status update of user_recipe in database."""
        
        recipe = get_recipe_by_url('test2.com')
        user = get_user('jhacks@gmail.com')
        mark_meal_made(recipe.recipe_id, user.user_id)
        user_recipe = UserRecipe.query.filter((UserRecipe.recipe_id == recipe.recipe_id) &
            (UserRecipe.user_id == user.user_id)).first()
        self.assertIsNotNone(user_recipe)
        self.assertFalse(user_recipe.active)
        self.assertTrue(user_recipe.times_cooked == 1)


    def test_get_score(self):
        """Test retrieval of score given user and recipe id."""
        
        user = get_user('jhacks@gmail.com')
        recipe = get_recipe_by_url('test1.com')

        score = get_score(recipe.recipe_id, user.user_id)
        self.assertIsNotNone(score)


    def test_upsert_score(self):
        """Test updating score record in database."""
         
        user = get_user('jhacks@gmail.com')
        recipe = get_recipe_by_url('test1.com')
        upsert_score(recipe.recipe_id, user.user_id, 1)
        updated_score = get_score(recipe.recipe_id, user.user_id)

        self.assertIsNotNone(updated_score)
        self.assertTrue(updated_score.score == 1)


################################################################################

if __name__ == "__main__":
    import unittest

    unittest.main()


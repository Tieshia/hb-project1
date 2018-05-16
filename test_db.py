from unittest import TestCase
from model import (User, Ingredient, StoredIngredient, Recipe, UserRecipe, Score,
    connect_to_db, db, example_data, example_data_update_meal)
from server import app
from seed import load_food_type
from flask import session

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


    def test_check_login(self):
        """Test login page w/ correct credentials."""

        result = self.client.post("/login",
                                data={'email': "jhacks@gmail.com",
                                'password': 'test'},
                                follow_redirects=True)
        self.assertIn('User Profile', result.data)
        self.assertIn('Welcome back', result.data)
        self.assertNotIn('Invalid credentials', result.data)


    def test_check_login_wrong_password(self):
        """Test login page w/ incorrect password."""

        result = self.client.post("/login",
                                data={'email': "jhacks@gmail.com",
                                'password': 'test?'},
                                follow_redirects=True)
        self.assertIn('Invalid credentials', result.data)
        self.assertIn('Log In', result.data)
        self.assertNotIn('User Profile', result.data)


    def test_check_login_wrong_email(self):
        """Test login page w/ incorrect email."""

        result = self.client.post('/login',
                            data={'email': 'test@gmail.com',
                            'password': 'test'},
                            follow_redirects=True)
        self.assertIn('Invalid credentials', result.data)
        self.assertIn('Log In', result.data)
        self.assertNotIn('User Profile', result.data)


    def test_registration_new_user(self):
        """Test adding new user from register page."""

        result = self.client.post('/register', 
                            data={'name': 'Sarah',
                            'email': 'sdevelops@gmail.com',
                            'password': 'test'},
                            follow_redirects=True)
        self.assertIn('Set Up', result.data)
        self.assertIn('name="ingredients"', result.data)
        self.assertNotIn('Invalid credentials', result.data)
        self.assertNotIn('Register', result.data)
        self.assertIsNotNone(User.query.filter_by(email='sdevelops@gmail.com').first())


    def test_registration_existing_user(self):
        """Test adding existing user from register page."""

        result = self.client.post('/register',
                            data={'name': 'Jane',
                            'email': 'jhacks@gmail.com',
                            'password': 'test'},
                            follow_redirects=True)
        self.assertNotIn('Set Up', result.data)
        self.assertIn('Invalid', result.data)
        self.assertIn('Register', result.data)
        self.assertTrue(len(User.query.filter_by(name='Jane').all()) == 1)

class FlaskTestsDatabaseLoggedIn(TestCase):
    """Flask database tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        
        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Add user to Flask session
        user = User.query.filter_by(name='Jane').first()
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = user.user_id


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()


    def test_create_profile(self):
        """Test adding ingredients to database from set up page."""

        result = self.client.post('/create-profile',
                            data={'ingredients': 'chicken,broccoli',
                                'types': 'Proteins,Produce'},
                            follow_redirects=True)
        self.assertIn('User Profile', result.data)
        self.assertIn('broccoli', result.data)
        self.assertIn('Protein', result.data)
        self.assertNotIn('Fritter', result.data)


    def test_user_profile(self):
        """Test actually loading user ingredients in db from session id."""

        result = self.client.get('/user-profile')

        self.assertIn('User Profile', result.data)
        self.assertIn('Produce', result.data)
        self.assertIn('steak', result.data)
        self.assertNotIn('chicken', result.data)
        self.assertIn('No recipes to display', result.data)
        self.assertNotIn('recipe1', result.data)


    def test_add_ingredients(self):
        """Test successfully adding ingredient input from user ingredients."""

        result = self.client.post('/add-ingredients',
                            data={'ingredients': 'spinach',
                            'types': 'Produce'},
                            follow_redirects=True)
        self.assertIn('Successfully added!', result.data)
        self.assertIn('spinach', result.data)
        self.assertIn('Produce', result.data)
        self.assertIsNotNone(Ingredient.query.filter_by(ingredient_name='spinach').first())
        self.assertTrue(len(Ingredient.query.filter_by(ingredient_name='spinach').all()) == 1)


    def test_remove_ingredients(self):
        """Test successfully removing ingredient input from user ingredients."""

        result = self.client.post('/remove-ingredients',
                                data={'ingredients': 'steak'},
                                follow_redirects=True)

        steak = Ingredient.query.filter_by(ingredient_name='steak').first()

        self.assertIn('Successfully deleted!', result.data)
        self.assertNotIn('steak', result.data)
        self.assertIsNone(StoredIngredient.query.filter_by(ingredient_id=steak.ingredient_id).first())
        self.assertIn('User Profile', result.data)


    def test_check_meal(self):
        """Test successfully adding items to meal plan."""

        recipe3 = Recipe(url='test3.com', image_url='test3_image.com',
                    recipe_name='recipe3')
        recipe4 = Recipe(url='test4.com', image_url='test4_image.com',
                    recipe_name='recipe4')
        db.session.add_all([recipe3, recipe4])
        db.session.commit()

        recipe3_id = str(recipe3.recipe_id)
        recipe4_id = str(recipe4.recipe_id)

        result = self.client.post('/check-meal',
                            data={'recipes': [recipe3_id, recipe4_id]},
                            follow_redirects=True)

        self.assertIn('Successfully added!', result.data)
        self.assertIsNotNone(UserRecipe.query.filter_by(recipe_id=int(recipe3_id)).first())
        self.assertIn('recipe3', result.data)
        self.assertNotIn('No recipes to display', result.data)


    def test_score_recipe(self):
        """Test successfully adding/updating user score for recipe."""

        # 
        user = User.query.filter_by(name='Jane').first()
        recipe = Recipe.query.filter_by(recipe_name='recipe1').first()
        user_score = Score.query.filter((Score.recipe_id == recipe.recipe_id) & 
            (Score.user_id == user.user_id))

        with self.client as c:
            with c.session_transaction() as sess:
                sess['recipe_id'] = recipe.recipe_id

        result = self.client.post('/score-recipe',
                            data={'effort': '1',
                            'taste': '-1'},
                            follow_redirects=True)

        
        updated_score = Score.query.filter((Score.recipe_id == recipe.recipe_id) & 
            (Score.user_id == user.user_id)).first()

        self.assertTrue(updated_score.taste_score == -1)
        self.assertIn('Successfully updated', result.data)


class FlaskTestsDatabaseLoggedInCheckedMeal(TestCase):
    """Flask database tests with user logged in to session."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        
        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add standard sample data
        db.create_all()
        example_data()

        # Add user to Flask session
        user = User.query.filter_by(name='Jane').first()
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = user.user_id

        # Add sample data for update_user_meal
        example_data_update_meal()


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_update_user_meal(self):
        """Test successfully updating UserRecipe once made."""

        recipe = Recipe.query.filter_by(recipe_name='recipe3').first()
        user_recipe = UserRecipe.query.filter_by(recipe_id=recipe.recipe_id).first()
        user_recipe_id = user_recipe.recipe_id
        user_recipe_id = str(user_recipe_id)

        result = self.client.post('/made-meal',
                            data={'recipe_id': user_recipe_id},
                            follow_redirects=True)

        used_recipe = UserRecipe.query.filter_by(recipe_id=int(user_recipe_id)).first()

        self.assertTrue(used_recipe.times_cooked == 1)
        self.assertFalse(used_recipe.times_cooked == 0)
        self.assertFalse(used_recipe.active)
        self.assertNotIn('recipe3', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()


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
from unittest import TestCase
import os
import json
from model import connect_to_db, db, example_data, User, Recipe
from server import app
import server
import bcrypt
from flask import session
from mealplan_db import get_recipe_by_url
import mealplan_recipes


class FlaskTestsBasic(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client.
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test homepage page."""

        result = self.client.get('/')
        self.assertIn('Welcome', result.data)
        self.assertIn('Log In', result.data)
        self.assertIn('Register', result.data)
        self.assertNotIn('User Profile', result.data)

    def test_login(self):
        """Test log in page."""

        result = self.client.get('/login')
        self.assertIn('Email', result.data)
        self.assertNotIn('Name', result.data)

    def test_register(self):
        """Test register page."""

        result = self.client.get('/register')
        self.assertIn('Name', result.data)
        self.assertNotIn('Log ', result.data)

    def test_logout(self):
        """Test logging out redirect with user not in session."""

        result = self.client.post('/logout', follow_redirects=True)
        self.assertIn('Welcome', result.data)
        self.assertIn('No user logged in.', result.data)
        self.assertNotIn('Goodbye!', result.data)


class FlaskRouteTestswDatabase(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client.
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Make mock response for highest rated recipe
        def _mock_get_random_highest_rated_recipes():
            """Makes mock return result for highest rated recipe."""
            recipe = get_recipe_by_url('test1.com')
            score = 4
            return [(score, recipe)]

        server.get_random_highest_rated_recipes = _mock_get_random_highest_rated_recipes

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

        self.assertIn('User Profile', result.data)
        self.assertNotIn('Invalid credentials', result.data)
        self.assertNotIn('Register', result.data)
        self.assertIn('No recipes to display', result.data)
        self.assertNotIn('I made this!', result.data)

    def test_registration_old_user(self):
        """Test adding old user from register page."""

        result = self.client.post('/register',
                                  data={'name': 'Jane',
                                        'email': 'jhacks@gmail.com',
                                        'password': 'test'},
                                  follow_redirects=True)
        self.assertIn('Invalid credentials', result.data)
        self.assertNotIn('User Profile', result.data)
        self.assertIn('Log In', result.data)


class FlaskRouteTestswDatabaseandSession(TestCase):
    """Flask tests requiring user in session."""

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        self.client = app.test_client()

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Add user to session
        user = User.query.filter_by(email='jhacks@gmail.com').first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = user.user_id

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_logout(self):
        """Test actually logging out user."""

        result = self.client.post('/logout', follow_redirects=True)
        self.assertIn('Goodbye', result.data)
        self.assertNotIn('User Profile', result.data)
        self.assertIn('Welcome', result.data)

    def test_user_profile(self):
        """Test actually loading user ingredients in db from session id."""

        result = self.client.get('/user-profile')

        self.assertIn('User Profile', result.data)
        self.assertIn('recipe2', result.data)
        self.assertNotIn('recipe3', result.data)

    def test_login_w_session(self):
        """Test login w user already in session."""

        result = self.client.get('/login', follow_redirects=True)

        self.assertIn('User Profile', result.data)
        self.assertIn('Already logged in', result.data)
        self.assertNotIn('Log In', result.data)

    def test_registration_w_session(self):
        """Test registration w user already in session."""

        result = self.client.get('/register', follow_redirects=True)

        self.assertIn('User Profile', result.data)
        self.assertNotIn('Log In', result.data)
        self.assertIn('User already logged in', result.data)

    def test_show_meals(self):
        """Test resulting recipes from API call."""

        # Make mock
        def _mock_get_recipes(params):
            """Makes mock API return result."""
            with open('static/edamam.txt') as json_file:
                data = json.load(json_file)
            return data['hits']

        mealplan_recipes.get_recipes = _mock_get_recipes

        result = self.client.post('/plan-meal', data={'app_id': os.environ.get('EDAMAM_SECRET_ID'),
                                                      'app_key': os.environ.get('EDAMAM_SECRET_KEY'),
                                                      'ingredients': ['chicken', 'broccoli'],
                                                      'types': ['Proteins', 'Produce']})

        self.assertIn('Chicken Broccoli Divan', result.data)
        self.assertIn('http://www.thekitchn.com/recipe-chicken-broccoli-alfredo-229203',
                      result.data)
        self.assertIn('<img', result.data)
        self.assertIn('</h3>', result.data)
        self.assertNotIn('Apple Fritter', result.data)

    def test_check_meal(self):
        """Test if meal checked being passed in to user profile."""

        recipe = Recipe.query.filter_by(url='test3.com').first()
        recipe_id = str(recipe.recipe_id)

        result = self.client.post('/check-meal', data={'recipes': [recipe_id]},
                                  follow_redirects=True)

        self.assertIn('test3', result.data)
        self.assertIn('Successfully added!', result.data)
        self.assertIn('User Profile', result.data)


################################################################################

if __name__ == "__main__":
    import unittest

    unittest.main()

from unittest import TestCase
import json
from model import (User, FoodType, Recipe, Ingredient, StoredIngredient,
    UserRecipe, Score, connect_to_db, db, example_data)
from server import app
import server

class MockFlaskTests(TestCase):
    """Flask tests that mock Spoonacular API response."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client.
        self.client = app.test_client()

        # Show Flask errors that happen during tests.
        app.config['TESTING'] = True

        # Connect to test database.
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data.
        db.create_all()
        example_data()

        # Make mock
        def _mock_get_recipes():
            """Makes mock API return result."""
            with open('spoonacular.txt') as json_file:
                data = json.load(json_file)
            return data

        server.get_recipes = _mock_get_recipes

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_get_recipes_with_mock(self):
        """Get results from Spoonacular API and show meal results."""

        result = self.client.post('/plan-meal', data={'ranking': 1,
                                                        'number': 5,
                                                        'ingredients': 'apples, sugar,flour'})

        self.assertIn('Apple Fritters', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
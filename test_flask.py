from unittest import TestCase
from model import connect_to_db, db, example_data
from server import app
from flask import session

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


    def test_login(self):
        """Test login page."""

        result = self.client.get('/login')
        self.assertIn('Log In', result.data)
        self.assertNotIn('Register', result.data)


    def test_register(self):
        """Test register page."""
        result = self.client.get('/register')
        self.assertIn('Register', result.data)
        self.assertNotIn('Log In', result.data)
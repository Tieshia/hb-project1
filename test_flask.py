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


    def test_create_profile(self):
        """Test create profile route."""

        result = self.client.get('/create-profile')
        self.assertIn('Set Up', result.data)
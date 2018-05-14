from unittest import TestCase
from model import User, connect_to_db, db, example_data
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
        self.assertNotIn('Fritter', result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()


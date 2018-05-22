from unittest import TestCase
from model import connect_to_db, db, example_data, User
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
        self.assertNotIn('Profile', result.data)


    def test_login(self):
        result = self.client.get('/login')
        self.assertIn('Email', result.data)
        self.assertNotIn('Name', result.data)


    def test_check_login(self):
        """Test login page w/ correct credentials."""

        result = self.client.post("/login",
                                data={'email': "jhacks@gmail.com",
                                'password': 'test'},
                                follow_redirects=True)
        self.assertIn('User Profile', result.data)
        self.assertIn('Welcome back', result.data)
        self.assertNotIn('Invalid credentials', result.data)


    # def test_check_login_wrong_password(self):
    #     """Test login page w/ incorrect password."""

    #     result = self.client.post("/login",
    #                             data={'email': "jhacks@gmail.com",
    #                             'password': 'test?'},
    #                             follow_redirects=True)
    #     self.assertIn('Invalid credentials', result.data)
    #     self.assertIn('Log In', result.data)
    #     self.assertNotIn('User Profile', result.data)


    # def test_check_login_wrong_email(self):
    #     """Test login page w/ incorrect email."""

    #     result = self.client.post('/login',
    #                         data={'email': 'test@gmail.com',
    #                         'password': 'test'},
    #                         follow_redirects=True)
    #     self.assertIn('Invalid credentials', result.data)
    #     self.assertIn('Log In', result.data)
    #     self.assertNotIn('User Profile', result.data)


    # def test_registration_new_user(self):
    #     """Test adding new user from register page."""

    #     result = self.client.post('/register', 
    #                         data={'name': 'Sarah',
    #                         'email': 'sdevelops@gmail.com',
    #                         'password': 'test'},
    #                         follow_redirects=True)

    #     self.assertIn('User Profile', result.data)
    #     self.assertNotIn('Invalid credentials', result.data)
    #     self.assertNotIn('Register', result.data)


# class FlaskTestLoggedIn:
#     """Flask tests requiring user in session."""

#     def setUp(self):
#         """Stuff to do before every test."""

#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'key'
#         self.client = app.test_client()

#         # Connect to test database
#         connect_to_db(app, "postgresql:///testdb")

#         # Create tables and add sample data
#         db.create_all()
#         example_data()

#         # Add user to session
#         user = User.query.filter_by(email='jhacks@gmail.com')

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['user'] = user.user_id


#     def test_logout(self):
#         """Test actually logging out user."""

#         result = self.client.post('/logout')

#         self.assertIn('Goodbye', result.py)


#     def test_user_profile(self):
#         """Test actually loading user ingredients in db from session id."""

#         result = self.client.get('/user-profile')

#         self.assertIn('User Profile', result.data)
#         self.assertIn('recipe2', result.data)
#         self.assertNotIn('recipe1', result.data)


################################################################################

if __name__ == "__main__":
    import unittest

    unittest.main()
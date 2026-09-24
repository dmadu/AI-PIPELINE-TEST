import unittest
from unittest.mock import patch, MagicMock
from app import app, db, User


class AAFAuthTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_redirect(self):
        response = self.app.get('/login')
        # Authlib authorize_redirect returns a redirect response
        self.assertIn(response.status_code, [302, 303])

    @patch('authlib.integrations.flask_client.OAuthRegistry.authorize_access_token')
    @patch('authlib.integrations.flask_client.OAuthRegistry.parse_id_token')
    def test_auth_callback_new_user_provisioning(self, mock_parse_id, mock_auth_token):
        mock_auth_token.return_value = {'access_token': 'fake-token'}
        mock_parse_id.return_value = {
            'email': 'newuser@example.com',
            'name': 'New Test User'
        }

        response = self.app.get('/auth/callback', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers['Location'])

        with app.app_context():
            user = User.query.filter_by(email='newuser@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'New Test User')
            self.assertEqual(user.role, 'VIEWER')

    @patch('authlib.integrations.flask_client.OAuthRegistry.authorize_access_token')
    @patch('authlib.integrations.flask_client.OAuthRegistry.parse_id_token')
    def test_auth_callback_existing_user(self, mock_parse_id, mock_auth_token):
        with app.app_context():
            existing = User(email='existing@example.com', name='Existing', role='ADMIN')
            db.session.add(existing)
            db.session.commit()

        mock_auth_token.return_value = {'access_token': 'fake-token'}
        mock_parse_id.return_value = {
            'email': 'existing@example.com',
            'name': 'Existing Updated'
        }

        response = self.app.get('/auth/callback', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        with app.app_context():
            users = User.query.filter_by(email='existing@example.com').all()
            self.assertEqual(len(users), 1)
            # Role should be preserved or remain unchanged
            self.assertEqual(users[0].role, 'ADMIN')


if __name__ == '__main__':
    unittest.main()

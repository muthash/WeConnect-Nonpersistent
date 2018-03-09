import unittest
import json
from app import create_app


class AuthTestCase(unittest.TestCase):
    """Test case for the user creation and login"""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.business = {
            'businessName': 'Kenya Power',
            'category': 'Lighting',
            'location': 'Nairobi'
        }
        self.edit_data = {
            'businessName': 'KenGen',
            'category': 'Geothrmal',
            'location': 'Nakuru'
        }

    def register_user(self, email="business@test.com", username="stephen",
                      password="test1234"):
        """This helper method helps register a test user."""
        user_data = {'email': email, 'username': username,
                     'password': password}
        return self.client().post(
                '/api/v1/register',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(user_data)
               )

    def login_user(self, email="business@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {'email': email, 'password': password}
        return self.client().post(
                '/api/v1/login',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(user_data)
               )

    def register_business(self, Name="KTDA", category="Farming",
                          location="Narok"):
        """This helper method helps register a test business"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        return self.client().post(
                '/api/v1/businesses',
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + access_token},
                data=json.dumps(self.business))

    def test_business_creation(self):
        """Test the API can create a bussiness (POST request)"""
        res = self.register_business()
        biz_Names = json.loads(res.data.decode())['business']
        self.assertIsInstance(biz_Names, list)
        self.assertTrue(biz_Names)
        self.assertIn("Kenya Power", biz_Names)
        self.assertEqual(res.status_code, 201)

    def test_get_all_businesses(self):
        """Test the API can create a bussiness (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(self.business)
        )
        res = self.client().get(
            '/api/v1/businesses',
            headers={'Authorization': 'Bearer ' + access_token}
        )
        biz = json.loads(res.data.decode())
        self.assertTrue(biz)
        self.assertEqual(res.status_code, 200)

    def test_api_can_get_business_by_id(self):
        """Test API can get a single business by using it's Id"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(self.business)
        )
        bizIds = json.loads(res.data.decode())['id']
        result2 = self.client().get(
            '/api/v1/businesses/{}'.format(bizIds[0]),
            headers={'Authorization': 'Bearer ' + access_token}
        )
        self.assertEqual(result2.status_code, 200)
        bizName = json.loads(result2.data.decode())['business']
        self.assertEqual('Kenya Power', bizName['name'])

    def test_business_can_be_edited(self):
        """Test API can edit an existing business. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(self.business)
        )
        bizIds = json.loads(res.data.decode())['id']
        result2 = self.client().put(
            '/api/v1/businesses/{}'.format(bizIds[0]),
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(self.edit_data)
        )
        bizName = json.loads(result2.data.decode())['business']
        self.assertEqual('KenGen', bizName['name'])
        self.assertEqual('Geothrmal', bizName['category'])
        self.assertEqual('Nakuru', bizName['location'])

    def test_business_delition(self):
        """Test API can delete an existing business. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(self.business)
        )
        bizIds = json.loads(res.data.decode())['id']
        res2 = self.client().delete(
            '/api/v1/businesses/{}'.format(bizIds[0]),
            headers={'Authorization': 'Bearer ' + access_token}
        )
        self.assertEqual(res2.status_code, 200)
        res3 = self.client().get(
            '/api/v1/businesses/{}'.format(bizIds[0]),
            headers={'Authorization': 'Bearer ' + access_token}
        )
        self.assertEqual(res3.status_code, 404)

    def test_invalid_business_name(self):
        """Test API can validate business name."""
        invalid_business = {
            'businessName': '       ',
            'category': 'Lighting',
            'location': 'Nairobi'
        }
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(invalid_business)
        )
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Invalid business name input")

    def test_invalid_access_token(self):
        """Test API can check for a valid access token"""
        valid_business = {
            'businessName': 'TRM',
            'category': 'Lighting',
            'location': 'Nairobi'
        }
        access_token = "dgeyfeyfye.hbyeye.hbeygeded"
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(valid_business)
        )
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Register to continue")

    def test_empty_access_token(self):
        """Test API can check for an empty access token"""
        valid_business = {
            'businessName': 'TRM',
            'category': 'Lighting',
            'location': 'Nairobi'
        }
        access_token = ""
        res = self.client().post(
            '/api/v1/businesses',
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer ' + access_token},
            data=json.dumps(valid_business)
        )
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Login in to continue")

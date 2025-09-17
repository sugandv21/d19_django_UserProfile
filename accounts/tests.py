# accounts/tests.py
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.cache import caches

class AccountsAPITestCase(APITestCase):
    def setUp(self):
        # Clear default cache to reset throttle counters between tests
        try:
            caches['default'].clear()
        except Exception:
            # If no cache configured or clear fails, ignore — tests will still run
            pass

        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.v1_profile_url = '/api/v1/profile/'
        self.v2_profile_url = '/api/v2/profile/'

        self.user_data = {'username': 'testuser', 'password': 'testpass123', 'email': 't@example.com'}
        resp = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.token = resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def tearDown(self):
        # Clear cache after each test as well, to be safe
        try:
            caches['default'].clear()
        except Exception:
            pass

    def test_unauthenticated_access(self):
        # remove credentials
        self.client.credentials()
        resp = self.client.get(self.v1_profile_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_v1(self):
        resp = self.client.get(self.v1_profile_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('user', resp.data)

    def test_update_profile_v1(self):
        resp = self.client.put(self.v1_profile_url, {'phone': '9999999999'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('phone'), '9999999999')

    def test_get_profile_v2_and_update_delete(self):
        resp = self.client.get(self.v2_profile_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # update bio
        resp2 = self.client.put(self.v2_profile_url, {'bio': 'hello v2', 'phone': '111'}, format='multipart')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data.get('bio'), 'hello v2')
        # delete profile (v2 supports destroy)
        resp3 = self.client.delete(self.v2_profile_url)
        self.assertIn(resp3.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))

    def test_throttle_exceed_user_rate(self):
        """
        Hammer the endpoint until throttle (429) is seen.
        The cache is cleared in setUp, so this test starts with a fresh quota.
        """
        exceeded = False
        # Try up to 60 times (should be plenty). Adjust if your throttle rates are very high.
        for i in range(60):
            resp = self.client.get(self.v1_profile_url)
            if resp.status_code == 429:
                exceeded = True
                break
        self.assertTrue(exceeded, "Expected to hit throttle limit (429) but did not.")

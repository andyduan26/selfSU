from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountAPITests(TestCase):
    def test_register_creates_user_with_hashed_password_and_returns_tokens(self):
        payload = {
            'username': 'student01',
            'nickname': '东方学员',
            'email': 'student01@example.com',
            'phone': '13800138000',
            'password': 'StrongPass123',
        }

        response = self.client.post('/api/auth/register/', data=payload, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        data = response.json()['data']
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['username'], 'student01')
        self.assertEqual(data['user']['nickname'], '东方学员')
        user = get_user_model().objects.get(username='student01')
        self.assertNotEqual(user.password, 'StrongPass123')
        self.assertTrue(user.check_password('StrongPass123'))

    def test_login_returns_jwt_and_current_user_profile_can_be_updated(self):
        user = get_user_model().objects.create_user(
            username='teacher01',
            nickname='东方老师',
            email='teacher01@example.com',
            phone='13900139000',
            password='StrongPass123',
        )

        login_response = self.client.post('/api/auth/login/', data={
            'username': 'teacher01',
            'password': 'StrongPass123',
        }, content_type='application/json')

        self.assertEqual(login_response.status_code, 200)
        access = login_response.json()['data']['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access}'

        me_response = self.client.get('/api/auth/me/')
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['data']['id'], user.id)
        self.assertTrue(me_response.json()['data']['registered_at'])

        update_response = self.client.put('/api/auth/me/', data={
            'nickname': '更新老师',
            'email': 'new-teacher01@example.com',
            'phone': '13700137000',
        }, content_type='application/json')

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()['data']['nickname'], '更新老师')
        user.refresh_from_db()
        self.assertEqual(user.email, 'new-teacher01@example.com')

# Create your tests here.

from django.test import TestCase


class HealthCheckAPITests(TestCase):
    def test_health_check_returns_unified_json(self):
        response = self.client.get('/api/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'code': 0,
            'message': 'success',
            'data': {
                'service': '东方知识库 API',
                'status': 'ok',
            },
        })


class JWTEndpointTests(TestCase):
    def test_token_endpoint_is_mounted(self):
        response = self.client.post('/api/auth/token/', data={}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json())
        self.assertIn('password', response.json())

# Create your tests here.

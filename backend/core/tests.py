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

# Create your tests here.

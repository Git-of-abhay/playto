from django.test import SimpleTestCase


class HealthEndpointTests(SimpleTestCase):
    def test_health_endpoint_is_machine_readable(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['version'], 2)

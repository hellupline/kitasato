import unittest

from werkzeug import exceptions, test as test_utils
from kitasato import MethodHandler


class Handler(MethodHandler):
    def get(self):
        return 'get'

    def post(self):
        return 'post'


class MethodHandlerTest(unittest.TestCase):
    def setUp(self):
        request = test_utils.EnvironBuilder().get_request()
        self.handler = Handler(None, request)

    def test_select_http_method_post(self):
        request = test_utils.EnvironBuilder(method='POST')
        value = Handler(None, request).entrypoint()
        self.assertEqual(value, 'post')

    def test_select_http_method_put(self):
        request = test_utils.EnvironBuilder(method='PUT')
        with self.assertRaises(exceptions.MethodNotAllowed):
            value = Handler(None, request).entrypoint()

    def test_select_http_method_get(self):
        value = self.handler.entrypoint()
        self.assertEqual(value, 'get')

    def test_get_allowed_methods(self):
        sample = {'GET': self.handler.get, 'POST': self.handler.post}
        allowed_methods = self.handler.get_allowed_methods()
        self.assertEqual(allowed_methods, sample)

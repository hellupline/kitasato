import unittest

from werkzeug import exceptions, test as test_utils

from kitasato import application, tree


class FakeResponse(tree.EndpointHandler):
    def dispatch_request(self, request):
        return 'ok'


class ApplicationTest(unittest.TestCase):
    def test_dispatch_request(self):
        root = application.Application(name='App', items=[
            FakeResponse(endpoint='fake', url='/')
        ])
        env = test_utils.EnvironBuilder(path='/')
        reply = root.dispatch_request(env.get_request())
        self.assertEqual(reply, 'ok')

    def test_dispatch_request_miss(self):
        root = application.Application(name='App', items=[])
        env = test_utils.EnvironBuilder(path='/miss')
        reply = root.dispatch_request(env.get_request())
        self.assertIsInstance(reply, exceptions.NotFound)

    def test_serve_endpoint(self):
        root = application.Application(name='App', items=[
            FakeResponse(endpoint='fake', url='/')
        ])
        reply = root.serve_endpoint(None, 'fake', {})
        self.assertEqual(reply, 'ok')

    def test_serve_endpoint_miss(self):
        root = application.Application(name='App', items=[])
        with self.assertRaises(exceptions.NotFound):
            reply = root.serve_endpoint(None, 'fake', {})

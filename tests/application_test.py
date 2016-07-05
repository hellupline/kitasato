import unittest

from werkzeug import exceptions, wrappers, test as test_utils

from taiga import Application, Tree, Leaf, EndpointHandler


class RootHandler(EndpointHandler):
    def entrypoint(self):
        return wrappers.Response('ok')


class ApplicationTest(unittest.TestCase):
    def setUp(self):
        self.app = Application(
            Leaf(endpoint='root', url='/', name='', handler=RootHandler),
        )
        self.request_miss = test_utils.EnvironBuilder(
            path='/miss').get_request()
        self.request = test_utils.EnvironBuilder(path='/').get_request()

    def test_endpoint_map(self):
        pass  # XXX: make test

    def test_url_map(self):
        pass  # XXX: make test

    def test_dispatch_request(self):
        reply = self.app.dispatch_request(self.request)
        self.assertEqual(reply.response, [b'ok'])

    def test_dispatch_request_miss(self):
        reply = self.app.dispatch_request(self.request_miss)
        self.assertIsInstance(reply, exceptions.NotFound)

    def test_serve_endpoint(self):
        reply = self.app.serve_endpoint(self.request, 'root', {})
        self.assertEqual(reply.response, [b'ok'])

    def test_serve_endpoint_miss(self):
        with self.assertRaises(exceptions.NotFound):
            reply = self.app.serve_endpoint(self.request_miss, 'miss', {})

    def test_get_url_for(self):
        url_for = self.app.get_url_for(self.request)
        self.assertEqual(url_for('root'), '/')

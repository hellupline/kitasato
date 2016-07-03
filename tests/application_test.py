import unittest

from werkzeug import exceptions, wrappers, test as test_utils

from kitasato import Application, Leaf, EndpointHandler


class RootHandler(EndpointHandler):
    def entrypoint(self):
        return wrappers.Response('ok')


class ApplicationTest(unittest.TestCase):
    def test_endpoint_map(self):
        pass  # XXX: make test

    def test_url_map(self):
        pass  # XXX: make test

    def test_dispatch_request(self):
        app = Application([
            Leaf(endpoint='root', url='/', name='', handler=RootHandler),
        ])
        env = test_utils.EnvironBuilder(path='/')
        reply = app.dispatch_request(env.get_request())
        self.assertEqual(reply.response, [b'ok'])

    def test_dispatch_request_miss(self):
        app = Application([])
        env = test_utils.EnvironBuilder(path='/miss')
        reply = app.dispatch_request(env.get_request())
        self.assertIsInstance(reply, exceptions.NotFound)

    def test_serve_endpoint(self):
        app = Application([
            Leaf(endpoint='root', url='/', name='', handler=RootHandler),
        ])
        reply = app.serve_endpoint(None, 'root', {})
        self.assertEqual(reply.response, [b'ok'])

    def test_serve_endpoint_miss(self):
        app = Application([])
        with self.assertRaises(exceptions.NotFound):
            reply = app.serve_endpoint(None, 'fake', {})

    def test_get_url_for(self):
        app = Application([
            Leaf(endpoint='root', url='/', name='', handler=RootHandler),
        ])
        env = test_utils.EnvironBuilder(path='/')
        url_for = app.get_url_for(env.get_request())
        self.assertEqual(url_for('root'), '/')

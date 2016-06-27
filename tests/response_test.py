import unittest

from werkzeug import wrappers, exceptions, test as test_utils

from kitasato import response


class App(response.RequestDispatcher):
    def dispatch_request(self, request):
        return wrappers.Response('ok')


class Render(response.RenderMixin):
    def context(self, resquest):
        return {'data': 'ok'}

    def render_html(self, context):
        return str(context['data'])

    render_json = render_html


class RequestDispacherTest(unittest.TestCase):
    def test_call(self):
        c = test_utils.Client(App())
        c.get('/')
        # XXX validate output


class RenderMixinTest(unittest.TestCase):
    def test_select_render_html(self):
        item = Render()
        env = test_utils.EnvironBuilder(path='/')
        item.dispatch_request(env.get_request(), render='json')
        # XXX validate output

    def test_select_render_miss(self):
        item = Render()
        env = test_utils.EnvironBuilder(path='/')
        with self.assertRaises(exceptions.NotFound):
            item.dispatch_request(env.get_request(), render='fake')

import unittest

from werkzeug import wrappers, exceptions, test as test_utils
import jinja2

from kitasato import response


class App(response.RequestDispatcher):
    def dispatch_request(self, request):
        return wrappers.Response('ok')


class Render(response.RenderMixin):
    template = jinja2.Template('{{ data }}')

    def context(self, resquest):
        return {'data': 'ok'}


class RequestDispacherTest(unittest.TestCase):
    def test_call(self):
        c = test_utils.Client(App())
        closing, status, headers = c.get('/')
        self.assertEqual(list(closing), [b'ok'])


class RenderMixinTest(unittest.TestCase):
    def test_select_render_html(self):
        request = test_utils.EnvironBuilder(path='/').get_request()
        response_html = Render().dispatch_request(request, render='html')
        self.assertEqual(response_html.response, [b'ok'])

    def test_select_render_json(self):
        request = test_utils.EnvironBuilder(path='/').get_request()
        response_json = Render().dispatch_request(request, render='json')
        self.assertEqual(response_json.response, [b'"ok"'])

    def test_select_render_miss(self):
        request = test_utils.EnvironBuilder(path='/').get_request()
        with self.assertRaises(exceptions.NotFound):
            Render().dispatch_request(request, render='fake')

import json

from werkzeug import wrappers, exceptions

HTTP_METHODS = {
    method: 'http_{}'.format(method.lower())
    for method in (
        'GET', 'POST', 'HEAD', 'OPTIONS',
        'DELETE', 'PUT', 'TRACE', 'PATCH',
    )
}


class RequestHandler:
    def __init__(self, application, request):
        self.application = application
        self.tree = application.tree
        self.request = request

    def initialize(self, **kwargs):
        pass

    def entrypoint(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def as_function(cls, **kwargs):
        def handler(application, request, **values):
            f = cls(application, request)
            f.initialize(**kwargs)
            return f.entrypoint(**values)
        return handler


class MethodHandler(RequestHandler):
    def entrypoint(self, *args, **kwargs):
        allowed_methods = self.get_allowed_methods()
        try:
            method = allowed_methods[self.request.method]
        except KeyError:
            valid_methods = list(allowed_methods.keys())
            raise exceptions.MethodNotAllowed(valid_methods)
        return method(*args, **kwargs)

    def get_allowed_methods(self):
        return {
            key: getattr(self, method_name)
            for key, method_name in HTTP_METHODS.items()
            if hasattr(self, method_name)
        }


class RenderHandler(MethodHandler):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.renders = {
            'html': self.render_html,
            'json': self.render_json,
        }

    def entrypoint(self, *args, render='html', **kwargs):
        try:
            render = self.renders[render]
        except KeyError:
            message = 'Stream render "{}" not found.'.format(render)
            raise exceptions.NotFound(message)
        body = super().entrypoint(*args, **kwargs)
        context = self.make_context(body=body)
        return wrappers.Response(render(context))

    def make_context(self, body=None):
        url_for = self.application.get_url_for(self.request)
        menu = self.application.tree.as_menu_tree()
        return {
            'request': self.request,
            'url_for': url_for,
            'menu': menu,
            **(body or {}),
        }

    def render_html(self, context):
        return self.get_template().render(**context)

    def get_template(self):
        raise NotImplementedError

    def render_json(self, context):
        return json.dumps(context['data'], indent=4)

import json

from werkzeug import wrappers, exceptions

HTTP_METHODS = (
    'GET', 'POST', 'HEAD', 'OPTIONS',
    'DELETE', 'PUT', 'TRACE', 'PATCH',
)


class EndpointHandler:
    def __init__(self, application, request):
        self.application = application
        self.request = request

    def entrypoint(self, *args, **kwargs):
        raise NotImplementedError()


class MethodHandler(EndpointHandler):
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
            key: getattr(self, key.lower())
            for key in HTTP_METHODS
            if hasattr(self, key.lower())
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
        url_for = self.application.get_url_for()
        return {
            'request': self.request,
            'url_for': url_for,
            **(body or {}),
        }

    def render_html(self, context):
        return self.template.render(**context)  # pylint: disable=no-member

    def render_json(self, context):
        return json.dumps(context['data'], indent=4)

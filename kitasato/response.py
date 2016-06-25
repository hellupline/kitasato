import json

from cached_property import cached_property

from werkzeug import wrappers, exceptions


class RequestDispatcher:
    def __call__(self, environ, start_response):
        response = self.dispatch_request(wrappers.Request(environ))
        return response(environ, start_response)

    def dispatch_request(self, request):
        raise NotImplementedError()


class RenderMixin:
    """A `dispatch_request` that renders from a `context` method."""

    def dispatch_request(self, request, *args, render='html', **kwargs):
        """Renders the output of `context` using `render` and returns.

        Returns:
            (Response): A Response object containing the response to request.
        """
        try:
            render = self.renders[render]
        except KeyError:
            msg = 'Stream render "{}" not found.'.format(render)
            raise exceptions.NotFound(msg)
        context = self.context(request, *args, **kwargs)
        return wrappers.Response(render(context))

    @cached_property
    def renders(self):
        return {
            'html': self.render_html,
            'json': self.render_json,
        }

    def render_html(self, context):
        return self.template.render(**context)

    def render_json(self, context):
        return json.dumps(context['data'], indent=4)

    def context(self, request):
        raise NotImplementedError()

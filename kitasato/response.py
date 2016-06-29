import json

from cached_property import cached_property

from werkzeug import wrappers, exceptions


class WSGIMixin:
    def __call__(self, environ, start_response):
        response = self.dispatch_request(wrappers.Request(environ))
        return response(environ, start_response)

    def dispatch_request(self, request):
        raise NotImplementedError()


class RenderMixin:
    """This class implements a `dispatch_request` and output renders.

    This `dispatch_request` will:
        - select a method based `request.method`, if method is missing
        raise MethodNotAllowed
        - select a render from `render` arg (default 'html'), if render
        is missing, raise NotFound
        - get the return of the method and pass to `self.context`
        - pass the return of the `self.context` to render
        - return the result of render
    """

    allowed_methods = {'GET': 'get', 'POST': 'post'}

    def dispatch_request(self, request, *args, render='html', **kwargs):
        """Renders the output of `get` or `post`,
        pass it to self.make_context
        and render using `render` and returns.

        Raises:
            MethodNotAllowed: if method not in `self.allowed_methods` or
                              if class method not exists
            NotFound: if render not in `self.renders`

        Returns:
            (Response): A Response object containing the response to request.
        """
        try:
            method = getattr(self, self.allowed_methods[request.method])
        except (KeyError, AttributeError):
            valid_methods = list(self.allowed_methods.keys())
            raise exceptions.MethodNotAllowed(valid_methods)
        try:
            render = self.renders[render]
        except KeyError:
            message = 'Stream render "{}" not found.'.format(render)
            raise exceptions.NotFound(message)

        body = method(request, *args, **kwargs)
        context = self.make_context(request, body=body)
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

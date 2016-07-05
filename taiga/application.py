from werkzeug import routing, wrappers, exceptions


class Application:
    """Handle WSGI requests with :class:`Tree`

    This class is a WSGI Application, will respond to urls on the `Tree`

    handlers should have the following signature
    >>> class RequestHandler:
    ...     def __init__(self, application, request):
    ...         ...
    ...     def entrypoint(self, **kwargs):
    ...         ...
    ...         return wrappers.Response(html)

    Arguments:
        tree (Tree): the tree with the urls and request handlers

    Attributes:
        url_map (Map): a `werkzeug.routing.Map` with the rules from
                       `tree.get_url_rules()`
        endpoint_map (dict): a endpoint -> handler mapping
        tree (Tree): the tree used to create the `url_map` and `endpoint_map`

    """
    def __init__(self, tree=None):
        self.url_map = routing.Map([tree.get_url_rules()])
        self.endpoint_map = dict(tree.get_endpoints())
        self.tree = tree

    def __call__(self, environ, start_response):  # pragma: no cover
        response = self.dispatch_request(wrappers.Request(environ))
        return response(environ, start_response)

    def dispatch_request(self, request):
        """Choose a `RequestHandler` to respond the request

        Arguments:
            request (werkzeug.wrappers.Request): werkzeug request wrapper

        Returns:
            the return value of the `RequestHandler.endpoint`,
            it should be a valid WSGI application
            eg: `werkzeug.wrappers.Response`
        """
        adapter = self.get_url_adapter(request)
        try:
            endpoint, values = adapter.match()
            return self.serve_endpoint(request, endpoint, values)
        except exceptions.NotFound as e:
            return e
        except exceptions.HTTPException as e:  # pragma: no cover
            return e

    def get_url_adapter(self, request):
        return self.url_map.bind_to_environ(request.environ)

    def get_url_for(self, request):
        return self.get_url_adapter(request).build

    def serve_endpoint(self, request, endpoint, values):
        try:
            handler_class = self.endpoint_map[endpoint]
        except KeyError:
            raise exceptions.NotFound('Endpoint not found.')
        handler = handler_class(self, request)
        return handler.entrypoint(**values)

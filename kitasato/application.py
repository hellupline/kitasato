from cached_property import cached_property
from werkzeug import routing, exceptions

from kitasato import tree, response

NO_ENDPOINT_MSG = 'Endpoint not found.'


class Application(response.RequestDispatcher, tree.Tree):
    def __init__(self, name, items):
        super().__init__(name=name, items=items)

    @cached_property
    def url_map(self):
        return routing.Map([self.get_url_rules()])

    @cached_property
    def endpoint_map(self):
        return dict(self.get_endpoints())

    def dispatch_request(self, request):
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

    def serve_endpoint(self, request, endpoint, values):
        try:
            handler = self.endpoint_map[endpoint]
        except KeyError:
            raise exceptions.NotFound(NO_ENDPOINT_MSG)
        return handler.dispatch_request(request, **values)

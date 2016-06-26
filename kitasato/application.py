from werkzeug import routing, exceptions

from kitasato import tree, response

NO_ENDPOINT_MSG = 'Endpoint not found.'


class Application(response.RequestDispatcher, tree.Tree):
    def __init__(self, name, items):
        super().__init__(name=name, items=items)
        self.url_map = routing.Map([self.get_url_rules()])
        self.endpoint_map = dict(self.get_endpoints())

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return self.respond_endpoint(request, endpoint, values)
        except exceptions.NotFound as e:
            return e
        except exceptions.HTTPException as e:
            return e

    def respond_endpoint(self, request, endpoint, values):
        try:
            handler = self.endpoint_map[endpoint]
        except KeyError:
            raise exceptions.NotFound(NO_ENDPOINT_MSG)
        return handler.dispatch_request(request, **values)

from pprint import pformat

from werkzeug import serving, wrappers

from kitasato import (
    Application, Tree, Leaf, EndpointHandler, Resource, ControllerMixin
)


class RootHandler(EndpointHandler):
    def entrypoint(self):
        return wrappers.Response('\n'.join([
            pformat(self.application.endpoint_map),
            pformat(self.application.url_map),
        ]))


def create_app():
    return Application(Tree(endpoint='', url='/', name='', items=[
        Resource(ControllerMixin(), endpoint='resource', url='/', name=''),
        Leaf(endpoint='index', url='/', name='', handler=RootHandler),
    ]))


if __name__ == '__main__':
    serving.run_simple('0.0.0.0', 5000, create_app(), use_reloader=True)

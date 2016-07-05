from pprint import pformat

from werkzeug import serving, wrappers

from taiga import (
    Application, Tree, Leaf, EndpointHandler, Resource, ControllerMixin
)


class RootHandler(EndpointHandler):
    def entrypoint(self):
        return wrappers.Response('\n'.join([
            pformat(self.application.endpoint_map),
            pformat(self.application.url_map),
        ]))


def create_tree():
    return Tree(endpoint='', url='/', name='', items=[
        Resource(ControllerMixin(), endpoint='resource', url='/', name=''),
        Leaf(endpoint='index', url='/', name='', handler=RootHandler),
    ])


if __name__ == '__main__':
    serving.run_simple(
        hostname='0.0.0.0',
        port=5000,
        application=Application(create_tree()),
        use_reloader=True,
        use_debugger=True,
    )

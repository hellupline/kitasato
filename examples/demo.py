from pprint import pformat

from werkzeug import serving, wrappers

from kitasato import application, tree, resource


class RootDocument(tree.EndpointHandler):
    endpoint = 'root_document'
    url = '/'
    name = 'Square'
    show_in_menu = True

    def dispatch_request(self, request):
        root = self.get_root()
        msg = '\n'.join([
            pformat(root.endpoint_map),  # pylint: disable=no-member
            pformat(root.url_map),  # pylint: disable=no-member
            pformat(root.as_menu_tree()),
        ])
        return wrappers.Response(msg)


def create_app():
    return application.Application(name='Root', items=[
        tree.Tree(url='/v1', endpoint='v1', name='V1', items=[
            RootDocument(name='V1 Root'),
        ]),
        RootDocument(),
        resource.Resource(url='/r1', endpoint='r1', name='Resource 1'),
    ])


if __name__ == '__main__':
    serving.run_simple('0.0.0.0', 5000, create_app(), use_reloader=True)

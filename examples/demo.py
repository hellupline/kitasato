from pprint import pformat

from werkzeug import serving, wrappers

from kitasato import application, tree, resource


class Index(tree.EndpointHandler):
    def dispatch_request(self, request):
        root = self.get_root()
        msg = '\n'.join([
            pformat(repr(root)),
            pformat(root.endpoint_map),
            pformat(root.url_map),
            pformat(root.as_menu_tree()),
        ])
        return wrappers.Response(msg)


def create_app():
    return application.Application(name='Root', items=[
        resource.Resource(url='/r1', endpoint='r1', name='Resource 1'),
        Index(url='/', endpoint='root_document', name='Square'),
    ])


if __name__ == '__main__':
    serving.run_simple('0.0.0.0', 5000, create_app(), use_reloader=True)

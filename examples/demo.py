from werkzeug import serving, wrappers
import jinja2
from kitasato import application, tree, resource

template = jinja2.Template(
    '''{% for name, value in data -%}
========================================
{{ name }}:
----------------------------------------
{{ value|pprint }}
{% endfor -%}
========================================

'''
)


class RootDocument(tree.EndpointHandler):
    endpoint = 'root_document'
    url = '/'
    name = 'Square'
    show_in_menu = True

    def dispatch_request(self, request):
        # pylint: disable=no-member
        root = self.get_root()
        url_for = root.get_url_adapter(request).build
        msg = template.render(data=[
            ('endpoint_map', root.endpoint_map),
            ('url_map', root.url_map),
            ('as_menu_tree', root.as_menu_tree()),
            ('url_for', ('r1:index', url_for('r1:index'))),
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

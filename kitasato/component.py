from math import ceil
import jinja2

from kitasato import tree, response


class Component(response.RenderMixin, tree.EndpointHandler):
    template = jinja2.Template(
        'request: {{ request }}\n'
        'url_for: {{ url_for }}\n'
    )

    @property
    def controller(self):
        return self.parent

    def make_context(self, request, body=None):
        url_for = self.get_root().get_url_for_func(request)  # noqa pylint: disable=no-member
        return {'request': request, 'url_for': url_for, **(body or {})}


class Index(Component):
    show_in_menu = True
    name = 'Index'
    url = '/index'
    endpoint = 'index'

    def get(self, request):
        page, order_by, reverse, filters = self._get_args(request)
        items, count = self.controller.get_items(
            page=page, order_by=order_by, reverse=reverse, filters=filters,
        )
        return {
            'pagination': self._get_pagination(count, page),
            'items': items, 'count': count,
        }

    def _get_args(self, request):
        args = dict(request.args)
        reverse = self._pop_args(args, 'reverse', default=False)
        reverse = bool(int(reverse))
        order_by = self._pop_args(args, 'order_by')
        page = self._pop_args(args, 'page', default=1)
        return page, order_by, reverse, args

    def _pop_args(self, args, key, default=None):
        try:
            return args.pop(key)
        except KeyError:
            return default

    def _get_pagination(self, count, page):
        per_page = self.controller.per_page
        if per_page == 0:
            pages = 0
        pages = ceil(count/per_page)
        return {'pages': pages, 'page': page}


class Create(Component):
    name = 'Create'
    url = '/create'
    endpoint = 'create'

    def get(self, request):
        return {}

    def post(self, request):
        item = self.controller.create_item(request.form)
        return {'item': item}


class Read(Component):
    name = 'Read'
    url = '/read/<key>'
    endpoint = 'read'

    def get(self, request, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}


class Update(Component):
    name = 'Update'
    url = '/update/<key>'
    endpoint = 'update'

    def get(self, request, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}

    def post(self, request, key):
        item = self.controller.get_item(key)
        self.controller.update_item(item, request.form)
        return {'item': item, 'key': key}


class Delete(Component):
    name = 'Delete'
    url = '/delete/<key>'
    endpoint = 'delete'

    def get(self, request, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}

    def post(self, request, key):
        item = self.controller.get_item(key)
        self.controller.delete_item(item)
        return {'item': item, 'key': key}

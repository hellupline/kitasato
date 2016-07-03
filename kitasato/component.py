from math import ceil
import jinja2

from kitasato import RenderHandler


class Component(RenderHandler):
    template = jinja2.Template(
        'request: {{ request }}\n'
        'url_for: {{ url_for }}\n'
    )
    controller = None


class Index(Component):
    show_in_menu = True

    def get(self):
        page, order_by, reverse, filters = self._get_args()
        items, count = self.controller.get_items(
            page=page, order_by=order_by, reverse=reverse, filters=filters,
        )
        return {
            'pagination': self._get_pagination(count, page),
            'items': items, 'count': count,
        }

    def _get_args(self):
        args = dict(self.request.args)
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
    def get(self):
        return {}

    def post(self):
        item = self.controller.create_item(self.request.form)
        return {'item': item}


class Read(Component):
    def get(self, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}


class Update(Component):
    def get(self, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}

    def post(self, key):
        item = self.controller.get_item(key)
        self.controller.update_item(item, self.request.form)
        return {'item': item, 'key': key}


class Delete(Component):
    def get(self, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}

    def post(self, key):
        item = self.controller.get_item(key)
        self.controller.delete_item(item)
        return {'item': item, 'key': key}

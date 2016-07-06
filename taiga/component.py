from math import ceil

import jinja2
from werkzeug import exceptions
from werkzeug.routing import Rule

from .response import RenderHandler


NOT_FOUND_MSG = 'Key {key} not found.'.format


"""
template vars:
    errors items item form

    request url_for menu
"""


class Component(RenderHandler):
    def get_template(self):
        return jinja2.Template(
            'Errors: {{ errors|pprint }}\n'
            'Items: {{ items|pprint }}\n'
            'Item: {{ item|pprint }}\n'
            'Menu:\n{{ menu|pprint }}\n'
            'Request: {{ request }}\n\n'
        )

    def initialize(self, controller, form):
        self.controller = controller
        self.form = form


class Index(Component):
    rule = Rule('/', endpoint='index', methods=('GET',))
    show_in_menu = True

    def http_get(self):
        page, order_by, reverse, filters = self._get_args()
        items, count = self.controller.get_items(
            page=page, order_by=order_by, reverse=reverse, filters=filters)
        return {
            'pagination': self.get_pagination(count, page),
            'items': items,
            'count': count,
        }

    def _get_args(self):
        args = dict(self.request.args)
        reverse = self._pop_args(args, 'reverse', default=False)
        order_by = self._pop_args(args, 'order_by')
        page = self._pop_args(args, 'page', default=1)
        return int(page), order_by, bool(int(reverse)), args

    def _pop_args(self, args, key, default=None):
        try:
            [value] = args.pop(key)
            return value
        except KeyError:
            return default

    def get_pagination(self, count, page):
        per_page = self.controller.per_page
        if per_page == 0:
            pages = 0
        pages = ceil(count/per_page)
        return {'pages': pages, 'page': page}


class Create(Component):
    rule = Rule('/create', endpoint='create', methods=('GET', 'POST'))
    show_in_menu = False

    def http_get(self):
        form = self.form()
        return {'form': form}

    def http_post(self):
        form = self.form(formdata=self.request.form)
        if not form.validate():
            return {'errors': form.errors, 'form': form}
        item = self.controller.create_item(form)
        return {'item': item}


class Read(Component):
    rule = Rule('/read/<key>', endpoint='read', methods=('GET',))
    show_in_menu = False

    def http_get(self, key):
        item = self.controller.get_item(key)
        if item is None:
            raise exceptions.NotFound(NOT_FOUND_MSG(key=key))
        return {'item': item, 'key': key}


class Update(Component):
    rule = Rule('/update/<key>', endpoint='update', methods=('GET', 'POST'))
    show_in_menu = False

    def http_get(self, key):
        item = self.controller.get_item(key)
        if item is None:
            raise exceptions.NotFound(NOT_FOUND_MSG(key=key))
        form = self.form(obj=item)
        return {'item': item, 'key': key, 'form': form}

    def http_post(self, key):
        item = self.controller.get_item(key)
        if item is None:
            raise exceptions.NotFound(NOT_FOUND_MSG(key=key))
        form = self.form(formdata=self.request.form, obj=item)
        if not form.validate():
            return {'errors': form.errors, 'form': form,
                    'item': item, 'key': key}
        self.controller.update_item(item, form)
        return {'item': item, 'key': key}


class Delete(Component):
    rule = Rule('/delete/<key>', endpoint='delete', methods=('GET', 'POST'))
    show_in_menu = False

    def http_get(self, key):
        item = self.controller.get_item(key)
        return {'item': item, 'key': key}

    def http_post(self, key):
        item = self.controller.get_item(key)
        self.controller.delete_item(item)
        return {'item': item, 'key': key}


class Action(Component):
    rule = Rule('/action/<key>', endpoint='action', methods=('POST',))
    show_in_menu = False

    def http_post(self, key):
        return {'key': key}

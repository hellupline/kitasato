from pprint import pformat

from werkzeug import serving, wrappers, routing
from wtforms import form as form_, fields, validators

from taiga import application, tree, response, resource, controller


class Form(form_.Form):
    value = fields.IntegerField(validators=[validators.Required()])


class MockModel(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MockController(controller.ControllerMixin):
    per_page = 5

    def __init__(self):
        self.items = {i: MockModel(key=i, value=i) for i in range(100)}
        self.next_key = 100

    def fetch_items(self):
        return list(self.items.values())

    def get_item(self, key):
        try:
            return self.items[int(key)]
        except KeyError:
            return None

    def create_item(self, form):
        item = self.items[self.next_key] = MockModel(key=self.next_key)
        self.next_key += 1
        self.update_item(item, form)
        return item

    def update_item(self, item, form):
        form.populate_obj(item)

    def delete_item(self, item):
        del self.items[item.key]


class RootHandler(response.RequestHandler):
    def entrypoint(self):
        return wrappers.Response('\n'.join([
            pformat(self.application.endpoint_map),
            pformat(self.application.url_map),
            pformat(self.tree.as_menu_tree()),
        ]))


def create_app():
    return application.Application(
        tree=tree.Tree(items=[
            resource.Resource(controller=MockController(), form=Form, url='/r', endpoint_key='r'),
            resource.Resource(controller=MockController(), form=Form, url='/s', endpoint_key='s'),
            tree.Leaf(
                handler=RootHandler.as_function(a=1),
                rule=routing.Rule('/', endpoint='root'),
            ),
        ])
    )

if __name__ == '__main__':
    serving.run_simple(
        hostname='0.0.0.0',
        port=5000,
        application=create_app(),
        use_reloader=True,
        use_debugger=True,
    )

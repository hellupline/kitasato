"""
    kitasato.resource
    ~~~~~~~~~~~~~~~~~

    controller-like class to create RPC interface.

    This module implements a simple RPC interface to help create HTTP APIs.
"""
import operator as op

from kitasato import tree, component


DEFAULT_COMPONENTS = (
    ('index', '/index', 'Index', True, component.Index),
    ('create', '/create', 'Create', False, component.Create),
    ('read', '/read/<key>', 'Read', False, component.Read),
    ('update', '/update/<key>', 'Update', False, component.Update),
    ('delete', '/delete/<key>', 'Delete', False, component.Delete),
)


class Resource(tree.Tree):  # pylint: disable=abstract-method
    """A RPC-like Tree Node

    This class is a :class:`kitasato.tree.Tree` with predetermined leafs,
    `kitasato.resource.DEFAULT_COMPONENTS`

    Arguments:
        controller (Controller): a controller to access storage methods,
                                 Controllers may use `ControllerMixin`
                                 as a base class
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        show_in_menu (bool): If node should be in menu_tree

    Attributes:
        components: contains the handlers that will respond to the request,
                    they `parent` will be this node.
                    its should be a iterable of tuples in the format:
                        (endpoint, url, name, show_in_menu, handler)
                    the default value is `kitasato.resource.DEFAULT_COMPONENTS`
        show_in_menu (bool): True if node should be in menu_tree, default True
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable node name
    """

    components = DEFAULT_COMPONENTS

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs, items=[
            tree.Leaf(
                endpoint=endpoint, url=url, handler=handler,
                name=name, show_in_menu=show_in_menu,
                # args={'controller': controller},
            )
            for endpoint, url, name, show_in_menu, handler in self.components
        ])


class ControllerMixin:
    per_page = 50
    filters = None

    def get_items(self, page=1, order_by=None, reverse=False, filters=None):
        """Combines the methods:
            - `fetch_items`
            - `filter_items`
            - `sort_items`
            - `slice_items`
            - `count_items`

        Arguments:
            page (int): the page number
            filters (sequence): a sequence of 2-items tuple of
                            (filter_key, value)
            order_by (str): the field to order items by
            reverse (bool): reverse the sort order,
                            only if order_by is not None
        """
        items = self.fetch_items()
        count = self.count_items(items)
        if filters is not None:
            items = self.filter_items(items, filters=filters)
        if order_by is not None:
            items = self.sort_items(items, order_by=order_by, reverse=reverse)
        items = self.slice_items(items, page=page)
        return items, count

    def filter_items(self, items, filters):
        """Filter items based on filters in `filters` attribute.

        Arguments:
            items (sequence): the items returned from `fetch_items`
            filters (sequence): a sequence of 2-items tuple of
                                (filter_key, value)
        Returns:
            list: filtered list
        """
        for filter_key, filter_value in filters.items():
            try:
                filter_func = self.filters[filter_key]
            except KeyError:
                continue
            items = filter_func(filter_value, items)
        return items

    def sort_items(self, items, order_by, reverse=False):
        """Sort items based on `order_by` key in items.

        Arguments:
            items (sequence): the items returned from `fetch_items`
            order_by (str): the field to order items by
            reverse (bool): reverse the sort order

        Returns:
            list: sorted items by `order_by`
        """
        return sorted(items, key=op.itemgetter(order_by), reverse=reverse)

    def slice_items(self, items, page=1):
        """Slice items in `per_page` items.

        Arguments:
            items (sequence): the items returned from `fetch_items`
            page (int): the page number

        Returns:
            list: slice of items
        """

        start, end = self.per_page*(page-1), self.per_page*page
        return items[start:end]

    def count_items(self, items):
        """Items size.

        Returns:
            int: len of items
        """
        return len(items)

    def fetch_items(self):
        raise NotImplementedError

    def get_item(self, pk):
        raise NotImplementedError

    def create_item(self, data):
        raise NotImplementedError

    def update_item(self, item, data):
        raise NotImplementedError

    def delete_item(self, item):
        raise NotImplementedError

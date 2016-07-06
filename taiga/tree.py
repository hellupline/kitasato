"""
    taiga.tree
    ~~~~~~~~~~

    Tree-like structure to create HTTP API.

    This module implements a simple tree-like structure to help create
    automated urls prefixes and endpoint prefixes.
"""
from werkzeug import routing

KEY_SEP = ':'


class Tree:
    """Implements a parent-child relationship for urls.

    Arguments:
        items (iterable[Tree]): Sequence of nodes
        endpoint_key (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        show_in_menu (bool): If node should be in menu_tree
    """

    parent = None

    def __init__(self, items=None, endpoint_key='', url='/',
                 name='', show_in_menu=True):
        self.endpoint_key = endpoint_key
        self.url = url
        self.items = []
        if items is not None:
            self.register_items(items)
        self.name = name
        self.show_in_menu = show_in_menu

    def __repr__(self):
        template = "<{cls_name} '{endpoint_key}' '{url}' '{name}'>"
        return template.format(
            cls_name=self.__class__.__name__,
            endpoint_key=self.absolute_endpoint_key(),
            url=self.absolute_url(),
            name=self.name,
        )

    def register_items(self, items):
        """Register items as this node children.

        Arguments:
            items (iterable[Tree]): Sequence of nodes
        """
        items = list(items)
        for item in items:
            item.set_parent(self)
        self.items.extend(items)

    def set_parent(self, parent):
        """Set parent node.

        Arguments:
            parent (Tree): Node to become parent of ``self``
        """
        self.parent = parent

    def get_url_rules(self):
        """Build a ``werkzeug.routiung.Rule`` for this node.

        Returns:
            werkzeug.routiung.Rule: A url Rule for this node
        """
        url_rules = [item.get_url_rules() for item in self.items]
        submount = [routing.Submount(self.url, url_rules)]
        prefix = ''
        if self.endpoint_key:
            prefix = ''.join([self.endpoint_key, KEY_SEP])
        return routing.EndpointPrefix(prefix, submount)

    def get_endpoints(self):
        """Yields all endpoints under this node.

        Yields:
            tuple: node endpoint (str) and the node
        """
        for item in self.items:
            yield from item.get_endpoints()

    def absolute_endpoint_key(self):
        """Concat parent endpoint_key with `self` endpoint_key

        Returns:
            str: the absolute endpoint_key
        """
        try:
            base = self.parent.absolute_endpoint_key()
        except AttributeError:
            return self.endpoint_key
        if not base:
            return self.endpoint_key
        return KEY_SEP.join([base, self.endpoint_key])

    def absolute_url(self):
        """Concat parent url with `self` url

        Returns:
            str: The absolute url
        """
        try:
            base = self.parent.absolute_url()
        except AttributeError:
            return self.url
        if not base:
            return self.url
        return '/'.join([base.rstrip('/'), self.url.lstrip('/')])

    def as_menu_tree(self):
        """Create a list with all nodes in a tree-like structure.

        Returns:
            dict: The tree-like structure
        """
        return {
            'endpoint_key': self.absolute_endpoint_key(),
            'name': self.name,
            'items': [
                item.as_menu_tree()
                for item in self.items
                if item.show_in_menu
            ],
        }


class Leaf(Tree):
    """Provide a entry in the tree for a ``EndpointHandler``

    the porpouse of this class is to be a description of the handler
    (endpoint name, url, name, show in menu).

    Arguments:
        handler (RequestHandler): A RequestHandler.
        rule (werkzeug.routiung.Rule): a url Rule.
        name (str): Human readable name.
        show_in_menu (bool): If node should be in menu_tree.
    """
    def __init__(self, handler, rule, name='', show_in_menu=True):
        endpoint_key, url = rule.endpoint, rule.rule
        super().__init__(
            items=(), endpoint_key=endpoint_key, url=url,
            name=name, show_in_menu=show_in_menu,
        )
        self.handler = handler
        self.rule = rule

    def get_url_rules(self):
        """Build a ``werkzeug.routiung.Rule`` for this node.

        Returns:
            werkzeug.routiung.Rule: A url Rule for this node
        """
        return self.rule.empty()

    def get_endpoints(self):
        """Returns this node endpoint and the handler.

        Returns:
            list (tuple): a list with one tuple in the format::
            (endpoint_key, (handler, handler_kwargs))
        """
        return [(self.absolute_endpoint_key(), self.handler)]

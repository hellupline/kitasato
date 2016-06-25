from werkzeug import routing


ENDPOINT_SEP = ':'


class Tree:
    """Implement a parent-child relationship for urls.

    Args:
        url (str): Url prefix for this node.
        endpoint (str): Endpoint prefix for this node.
        name (str): Human readable node name.
        items (Optional[iterable[Tree]]): Sequence of nodes.

    Attributes:
        url (str): Url prefix for this node.
        endpoint (str): Endpoint prefix for this node.
        name (str): Human readable node name.
        items (list): A list with children nodes.
    """
    parent = items = url = endpoint = name = None
    show_in_menu = True

    def __init__(self, url=None, endpoint=None, name=None, items=None):
        if endpoint is not None:
            self.endpoint = endpoint
        if url is not None:
            self.url = url
        if name is not None:
            self.name = name
        self.items = []
        if items is not None:
            self.register_items(items)

    def __repr__(self):
        templ = '<{cls_name} url="{url}" endpoint="{endpoint}" name="{name}">'
        return templ.format(
            cls_name=self.__class__.__name__,
            url=self.url, endpoint=self.endpoint, name=self.name,
        )

    def register_items(self, items):
        """Register items as this node children.

        Args:
            items (iterable[Tree]): Sequence of nodes.
        """
        for item in items:
            item.set_parent(self)
        self.items.extend(items)

    def set_parent(self, parent):
        """Set parent node.

        Args:
            parent (Tree): Node to become parent of `self`
        """
        self.parent = parent

    def get_root(self):
        """Get root node.

        Returns:
            (Tree): the root node of node.
        """
        if self.is_root():
            return self
        return self.parent.get_root()

    def is_root(self):
        """Check if node is root node.

        Returns:
            (bool): True if node is a root node.
        """
        return self.parent is None


class Path(Tree):
    """Contains the methods to render a tree into a menu."""

    def get_endpoints(self):
        """Yields all endpoints under this node.

        Yields:
            (tuple): Tuple containing:
                (str): node endpoint.
                (Tree): node.

        """
        for item in self.items:
            yield from item.get_endpoints()

    def get_url_rules(self):
        """Build a UrlRule for this node.

        Returns:
            (UrlRule): A UrlRule for this node.
        """
        url_rules = [item.get_url_rules() for item in self.items]
        prefix = ''
        if self.endpoint:
            prefix = ''.join([self.endpoint, ENDPOINT_SEP])
        if self.url:
            url_rules = [routing.Submount(self.url, url_rules)]
        return routing.EndpointPrefix(prefix, url_rules)

    def as_menu_tree(self):
        """Create a list with all nodes in a tree-like structure.

        Returns:
            (list): the tree-like structure.
        """
        return {
            'endpoint': self.absolute_endpoint(),
            'name': self.name,
            'items': [
                item.as_menu_tree()
                for item in self.items
                if item.show_in_menu
            ],
        }

    def absolute_endpoint(self):
        """Concat parent endpoint with `self` endpoint

        Returns:
            (str): the absolute endpoint.
        """
        try:
            base = self.parent.absolute_endpoint()
        except AttributeError:
            return self.endpoint
        if not base:
            return self.endpoint
        return ENDPOINT_SEP.join([base, self.endpoint])


class EndpointHandler(Path):
    show_in_menu = False
    """bool: True if node should be in menu_tree, default False."""

    def get_url_rules(self):
        return routing.Rule(self.url, endpoint=self.endpoint)

    def get_endpoints(self):
        return [(self.absolute_endpoint(), self)]

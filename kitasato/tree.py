"""
    kitasato.tree
    ~~~~~~~~~~~~~

    Tree-like structure to create HTTP API.

    This module implements a simple tree-like structure to help create
    automated urls prefixes and endpoint prefixes.

    Example:
        >>> from kitasato import application, tree, resource
        >>> from werkzeug import serving, wrappers
        >>> class RootDocument(tree.EndpointHandler):
        ...     def dispatch_request(self, request):
        ...         root = self.get_root()
        ...         msg = ', '.join([
        ...             pformat(root.endpoint_map),
        ...             pformat(root.url_map),
        ...             pformat(root.as_menu_tree()),
        ...         ])
        ...         return wrappers.Response(msg)
        >>> def create_app():
        ...     return application.Application(name='API', items=[
        ...         tree.Tree(url='/v1', endpoint='api-v1', name='V1', items=[
        ...             RootDocument(
        ...                 url='/', endpoint='example', name='Example'),
        ...         ]),
        ...     ])
        >>> if __name__ == '__main__':
        ...     serving.run_simple('0.0.0.0', 5000, create_app())
"""
from werkzeug import routing

ENDPOINT_SEP = ':'


class Tree:
    """Implements a parent-child relationship for urls.

    Arguments:
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        items (iterable[Tree]): Sequence of nodes
        show_in_menu (bool): If node should be in menu_tree

    Attributes:
        show_in_menu (bool): True if node should be in menu_tree, default True
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable node name
        items (list): A list with children nodes
    """
    parent = items = endpoint = url = name = None
    show_in_menu = True

    def __init__(self, endpoint=None, url=None, name=None, items=None,
                 show_in_menu=None):
        values = locals()
        for attr in ('endpoint', 'url', 'name', 'show_in_menu'):
            if values[attr] is not None:
                setattr(self, attr, values[attr])
        self.items = []
        if items is not None:
            self.register_items(items)

    def __repr__(self):
        templ = '<{cls_name} endpoint="{endpoint}" url="{url}" name="{name}">'
        return templ.format(
            cls_name=self.__class__.__name__,
            endpoint=self.absolute_endpoint(),
            url=self.absolute_url(),
            name=self.name,
        )

    def register_items(self, items):
        """Register items as this node children.

        Arguments:
            items (iterable[Tree]): Sequence of nodes
        """
        for item in items:
            item.set_parent(self)
        self.items.extend(items)

    def set_parent(self, parent):
        """Set parent node.

        Arguments:
            parent (Tree): Node to become parent of `self`
        """
        self.parent = parent

    def get_root(self):
        """Get root node.

        Returns:
            Tree: the root node of node
        """
        if self.is_root():
            return self
        return self.parent.get_root()

    def is_root(self):
        """Check if node is root node.

        Returns:
            bool: True if node is a root node
        """
        return self.parent is None

    def get_url_rules(self):
        """Build a Rule for this node.

        Returns:
            werkzeug.routiung.Rule: A url Rule for this node
        """
        url_rules = [item.get_url_rules() for item in self.items]
        prefix = ''
        if self.endpoint:
            prefix = ''.join([self.endpoint, ENDPOINT_SEP])
        if self.url:
            url_rules = [routing.Submount(self.url, url_rules)]
        return routing.EndpointPrefix(prefix, url_rules)

    def get_endpoints(self):
        """Yields all endpoints under this node.

        Yields:
            tuple: node endpoint (str) and the node
        """
        for item in self.items:
            yield from item.get_endpoints()

    def absolute_endpoint(self):
        """Concat parent endpoint with `self` endpoint

        Returns:
            str: the absolute endpoint
        """
        try:
            base = self.parent.absolute_endpoint()
        except AttributeError:
            return self.endpoint
        if not base:
            return self.endpoint
        return ENDPOINT_SEP.join([base, self.endpoint])

    def absolute_url(self):
        """Concat parent url with `self` url

        Returns:
            str: the absolute url
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
            list: the tree-like structure
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


class EndpointHandler(Tree):
    """EndpointHandler implements the response wrapper for the tree structure.

    Overwrite `dispatch_request` to return a `werkzeug.wrapper.Response`.

    Here is a example:

        >>> from werkzeug import wrappers
        >>> from kitasato import tree
        >>> class Document(tree.EndpointHandler):
        ...     def dispatch_request(self, request, *args, **kwargs):
        ...         return wrappers.Response('Hello World', status=200)

    Arguments:
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        show_in_menu (bool): If node should be in menu_tree

    Attributes:
        show_in_menu (bool): True if node should be in menu_tree, default False
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable node name

    Methods:
        dispatch_request: Ovewrite this method to implement the response
                          function
    """
    show_in_menu = False

    def __init__(self, endpoint=None, url=None, name=None, show_in_menu=None):
        super().__init__(
            endpoint=endpoint, url=url, name=name, show_in_menu=show_in_menu,
        )

    def get_url_rules(self):
        """Build a Rule for this node.

        Returns:
            werkzeug.routiung.Rule: A url Rule for this node
        """
        return routing.Rule(self.url, endpoint=self.endpoint)

    def get_endpoints(self):
        """Returns this node endpoint and the node itself.

        Returns:
            list (tuple): node endpoint (str) and the node
        """
        return [(self.absolute_endpoint(), self)]

    def dispatch_request(self):
        raise NotImplementedError()

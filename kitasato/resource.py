"""
    kitasato.resource
    ~~~~~~~~~~~~~~~~~

    controller-like class to create RPC interface.

    This module implements a simple RPC interface to help create HTTP APIs.
"""
from kitasato import tree, component


class Resource(tree.Tree):
    """Simple RPC APIs may implements a CRUD interface.

    This class is a :class:`kitasato.tree.Tree` with predetermined items:
        - :class:`kitasato.component.Index`
        - :class:`kitasato.component.Create`
        - :class:`kitasato.component.Read`
        - :class:`kitasato.component.Update`
        - :class:`kitasato.component.Delete`

    Arguments:
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        show_in_menu (bool): If node should be in menu_tree

    Attributes:
        components: contains the components that will be initiated,
                    they `parent` will be this node, may be overwriten to
                    change components
        show_in_menu (bool): True if node should be in menu_tree, default True
        endpoint (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable node name
    """

    components = (
        component.Index,
        component.Create,
        component.Read,
        component.Update,
        component.Delete,
    )

    def __init__(self, endpoint=None, url=None, name=None, show_in_menu=None):
        super().__init__(
            endpoint=endpoint, url=url, name=name, show_in_menu=show_in_menu,
            items=(component() for component in self.components),
        )

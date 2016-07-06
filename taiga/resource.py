"""
    taiga.resource
    ~~~~~~~~~~~~~~

    controller-like class to create RPC interface.

    This module implements a simple RPC interface to help create HTTP APIs.
"""
from taiga.component import Index, Create, Read, Update, Delete, Action
from taiga.tree import Tree, Leaf


DEFAULT_COMPONENTS = (
    (Index, {'rule': Index.rule, 'name': 'Index',
             'show_in_menu': Index.show_in_menu}),
    (Create, {'rule': Create.rule, 'name': 'Create',
              'show_in_menu': Create.show_in_menu}),
    (Read, {'rule': Read.rule, 'name': 'Read',
            'show_in_menu': Read.show_in_menu}),
    (Update, {'rule': Update.rule, 'name': 'Update',
              'show_in_menu': Update.show_in_menu}),
    (Delete, {'rule': Delete.rule, 'name': 'Delete',
              'show_in_menu': Delete.show_in_menu}),
    (Action, {'rule': Action.rule, 'name': 'Action',
              'show_in_menu': Action.show_in_menu}),
)


class Resource(Tree):  # pylint: disable=abstract-method
    """A RPC-like Tree Node

    This class is a :class:``taiga.tree.Tree`` with predetermined leafs,
    ``taiga.resource.DEFAULT_COMPONENTS``

    Arguments:
        controller (Controller): a controller to access storage methods,
            Controllers may use ``ControllerMixin`` as a base class
        endpoint_key (str): Endpoint prefix for this node
        url (str): Url prefix for this node
        name (str): Human readable name
        show_in_menu (bool): If node should be in menu_tree

    Attributes:
        components: contains the handlers that will respond to the request,
            they `parent` will be this node. Each entry should be a
            kwargs style dict for the ``Leaf`` class.
            The default value is ``taiga.resource.DEFAULT_COMPONENTS``
    """

    components = DEFAULT_COMPONENTS

    def __init__(self, controller, form,
                 endpoint_key='resource', url='/',
                 name='', show_in_menu=True):
        handler_kwargs = {'controller': controller, 'form': form}
        items = [
            Leaf(handler.as_function(**handler_kwargs), **leaf_kwargs)
            for handler, leaf_kwargs in self.components
        ]
        super().__init__(
            items=items, endpoint_key=endpoint_key, url=url,
            name=name, show_in_menu=show_in_menu,
        )

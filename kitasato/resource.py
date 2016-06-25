from kitasato import tree, component


class Resource(tree.Path):
    components = (
        component.Index,
        component.Create,
        component.Read,
        component.Update,
        component.Delete,
    )

    def __init__(self, url=None, endpoint=None, name=None):
        items = [component() for component in self.components]
        super().__init__(url=url, endpoint=endpoint, name=name, items=items)

import unittest

from kitasato import tree


class TreeTest(unittest.TestCase):
    def _create_node(self, i=0, items=None):
        name = 'level{}'.format(i)
        url = '/{}'.format(name)
        return tree.Tree(
            endpoint=name, url=url, name=name,
            show_in_menu=True, items=items,
        )

    def test_register_items(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node()
        root.register_items(items)
        for item in items:
            self.assertEqual(root, item.parent)
            self.assertIn(item, root.items)
        self.assertEqual(root.items, items)

    def test_set_parent(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node()
        for item in items:
            item.set_parent(root)
            self.assertEqual(root, item.parent)

    def test_init_with_items(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        for item in items:
            self.assertEqual(root, item.parent)
            self.assertIn(item, root.items)

    def test_get_root(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = self._create_node(items=[level1])
        self.assertIs(level2.get_root(), root)

    def test_is_root(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        for item in items:
            self.assertFalse(item.is_root())
        self.assertTrue(root.is_root())

    def test_get_url_rules(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        rule = root.get_url_rules()
        self.assertEqual(rule.prefix, 'level0:')
        self.assertEqual(rule.rules[0].path, '/level0')

    def test_get_url_rules_no_endpoint(self):
        items = [self._create_node(i) for i in range(2)]
        root = tree.Tree(url='/level0/', items=items)
        rule = root.get_url_rules()
        self.assertEqual(rule.prefix, '')
        self.assertEqual(rule.rules[0].path, '/level0')

    def test_get_endpoints(self):
        node = tree.EndpointHandler(
            endpoint='node', url='/node', name='node', show_in_menu=True
        )
        root = self._create_node(items=[node])
        endpoints = list(root.get_endpoints())
        sample = [('level0:node', node)]
        self.assertEqual(node.get_endpoints(), sample)

    def test_absolute_endpoint(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = self._create_node(items=[level1])
        self.assertEqual(level2.absolute_endpoint(), 'level0:level1:level2')
        self.assertEqual(level1.absolute_endpoint(), 'level0:level1')
        self.assertEqual(root.absolute_endpoint(), 'level0')

    def test_absolute_endpoint_no_base_endpoint(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = tree.Tree(items=[level1])
        self.assertEqual(level2.absolute_endpoint(), 'level1:level2')
        self.assertEqual(level1.absolute_endpoint(), 'level1')
        self.assertEqual(root.absolute_endpoint(), None)

    def test_absolute_url(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = self._create_node(items=[level1])
        self.assertEqual(level2.absolute_url(), '/level0/level1/level2')
        self.assertEqual(level1.absolute_url(), '/level0/level1')
        self.assertEqual(root.absolute_url(), '/level0')

    def test_absolute_url_no_base_url(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = tree.Tree(items=[level1])
        self.assertEqual(level2.absolute_url(), '/level1/level2')
        self.assertEqual(level1.absolute_url(), '/level1')
        self.assertEqual(root.absolute_url(), None)

    def test_as_menu_tree(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        sample = {
            'items': [{
                'endpoint': item.absolute_endpoint(),
                'name': item.name, 'items': [],
            } for item in items],
            'endpoint': 'level0', 'name': 'level0',
        }
        self.assertEqual(root.as_menu_tree(), sample)

    def test_as_menu_tree_empty(self):
        root = self._create_node()
        sample = {'endpoint': 'level0', 'name': 'level0', 'items': []}
        self.assertEqual(root.as_menu_tree(), sample)


class EndpointHandlerTest(unittest.TestCase):
    def _create_node(self, i=0):
        name = 'level{}'.format(i)
        url = '/{}'.format(name)
        return tree.EndpointHandler(
            endpoint=name, url=url, name=name, show_in_menu=True,
        )

    def test_get_url_rules(self):
        node = self._create_node()
        rule = node.get_url_rules()
        self.assertEqual(rule.rule, '/level0')
        self.assertEqual(rule.endpoint, 'level0')

    def test_get_endpoints(self):
        node = self._create_node()
        self.assertEqual(node.get_endpoints(), [('level0', node)])

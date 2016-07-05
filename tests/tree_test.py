import unittest

from taiga import Tree, Leaf


class TreeTest(unittest.TestCase):
    def _create_node(self, i=0, items=None):
        name = 'level-{}'.format(i)
        url = '/{}'.format(name)
        return Tree(
            endpoint=name, url=url, items=items,
            name=name, show_in_menu=True,
        )

    def _create_leaf(self, i=0):
        name = 'level-{}'.format(i)
        url = '/{}'.format(name)
        return Leaf(
            endpoint=name, url=url, handler=None,
            name=name, show_in_menu=True,
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

    def test_get_url_rules(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        rule = root.get_url_rules()
        self.assertEqual(rule.prefix, 'level-0:')
        self.assertEqual(rule.rules[0].path, '/level-0')

    def test_get_url_rules_no_endpoint(self):
        items = [self._create_node(i) for i in range(2)]
        root = Tree(endpoint='', url='/level-0', name='', items=items)
        rule = root.get_url_rules()
        self.assertEqual(rule.prefix, '')
        self.assertEqual(rule.rules[0].path, '/level-0')

    def test_get_endpoints(self):
        root = self._create_node(items=[self._create_leaf()])
        sample = [('level-0:level-0', None)]
        self.assertEqual(list(root.get_endpoints()), sample)

    def test_absolute_endpoint(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = self._create_node(items=[level1])
        self.assertEqual(level2.absolute_endpoint(), 'level-0:level-1:level-2')
        self.assertEqual(level1.absolute_endpoint(), 'level-0:level-1')
        self.assertEqual(root.absolute_endpoint(), 'level-0')

    def test_absolute_endpoint_no_base_endpoint(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = Tree(endpoint='', url='', name='', items=[level1])
        self.assertEqual(level2.absolute_endpoint(), 'level-1:level-2')
        self.assertEqual(level1.absolute_endpoint(), 'level-1')
        self.assertEqual(root.absolute_endpoint(), '')

    def test_absolute_url(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = self._create_node(items=[level1])
        self.assertEqual(level2.absolute_url(), '/level-0/level-1/level-2')
        self.assertEqual(level1.absolute_url(), '/level-0/level-1')
        self.assertEqual(root.absolute_url(), '/level-0')

    def test_absolute_url_no_base_url(self):
        level2 = self._create_node(2)
        level1 = self._create_node(1, items=[level2])
        root = Tree(endpoint='', url='', name='', items=[level1])
        self.assertEqual(level2.absolute_url(), '/level-1/level-2')
        self.assertEqual(level1.absolute_url(), '/level-1')
        self.assertEqual(root.absolute_url(), '')

    def test_as_menu_tree(self):
        items = [self._create_node(i) for i in range(2)]
        root = self._create_node(items=items)
        sample = {
            'items': [{
                'endpoint': item.absolute_endpoint(),
                'name': item.name, 'items': [],
            } for item in items],
            'endpoint': 'level-0', 'name': 'level-0',
        }
        self.assertEqual(root.as_menu_tree(), sample)

    def test_as_menu_tree_empty(self):
        root = self._create_node()
        sample = {'endpoint': 'level-0', 'name': 'level-0', 'items': []}
        self.assertEqual(root.as_menu_tree(), sample)


class LeafTest(unittest.TestCase):
    def _create_leaf(self, i=0):
        name = 'level-{}'.format(i)
        url = '/{}'.format(name)
        return Leaf(
            endpoint=name, url=url, handler=None,
            name=name, show_in_menu=True,
        )

    def test_url_rules(self):
        rule = self._create_leaf().get_url_rules()
        self.assertEqual(rule.rule, '/level-0')

    def test_get_endpoints(self):
        endpoints = self._create_leaf().get_endpoints()
        self.assertEqual(list(endpoints), [('level-0', None)])

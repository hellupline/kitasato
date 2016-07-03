import unittest

from kitasato import (
    Resource, Index, Create, Read, Update, Delete, ControllerMixin)


def filter_0(value, items):
    return [item for item in items if item[0] == value]


def filter_1(value, items):
    return [item for item in items if item[1] == value]


class Controller(ControllerMixin):  # pylint: disable=abstract-method
    filters = {'0': filter_0, '1': filter_1}
    per_page = 2

    def fetch_items(self):
        return [
            ('a', 0), ('a', 1), ('a', 2), ('a', 3),
            ('b', 0), ('b', 1), ('b', 2), ('b', 3),
            ('c', 0), ('c', 1), ('c', 2), ('c', 3),
            ('d', 0), ('d', 1), ('d', 2), ('d', 3),
        ]


class ResourceTest(unittest.TestCase):
    def test_init_components(self):
        resource = Resource(None, endpoint='res', url='/', name='Res')
        sample = [
            ('res:index', Index),
            ('res:create', Create),
            ('res:read', Read),
            ('res:update', Update),
            ('res:delete', Delete),
        ]
        self.assertEqual(list(resource.get_endpoints()), sample)


class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = Controller()
        self.items = self.controller.fetch_items()

    def test_filter_items(self):
        items = self.controller.filter_items(self.items, {'0': 'a'})
        self.assertEqual(items, [('a', 0), ('a', 1), ('a', 2), ('a', 3)])

    def test_filter_items_multiple_filters(self):
        items = self.controller.filter_items(self.items, {'0': 'a', '1': 0})
        self.assertEqual(items, [('a', 0)])

    def test_sort_items(self):
        sample = [
            ('a', 0), ('b', 0), ('c', 0), ('d', 0),
            ('a', 1), ('b', 1), ('c', 1), ('d', 1),
            ('a', 2), ('b', 2), ('c', 2), ('d', 2),
            ('a', 3), ('b', 3), ('c', 3), ('d', 3),
        ]
        items = self.controller.sort_items(self.items, 1)
        self.assertEqual(items, sample)

    def test_slice_items_reverse(self):
        sample = [
            ('a', 3), ('b', 3), ('c', 3), ('d', 3),
            ('a', 2), ('b', 2), ('c', 2), ('d', 2),
            ('a', 1), ('b', 1), ('c', 1), ('d', 1),
            ('a', 0), ('b', 0), ('c', 0), ('d', 0),
        ]
        items = self.controller.sort_items(self.items, 1, reverse=True)
        self.assertEqual(items, sample)

    def test_slice_items(self):
        items = self.controller.slice_items(self.items, page=2)
        self.assertEqual(items, [('a', 2), ('a', 3)])

    def test_count_items(self):
        count = self.controller.count_items(self.items)
        self.assertEqual(count, len(self.items))

    def test_get_items(self):
        items, count = self.controller.get_items(
            page=2, order_by=1, reverse=True, filters={'0': 'a'}
        )
        self.assertEqual(items, [('a', 1), ('a', 0)])
        self.assertEqual(count, len(self.items))

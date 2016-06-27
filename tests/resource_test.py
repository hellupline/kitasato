import unittest

from kitasato import resource, tree


class ResourceTest(unittest.TestCase):
    def test_init_components(self):
        node = resource.Resource()
        for item in node.items:
            self.assertIsInstance(item, tree.EndpointHandler)

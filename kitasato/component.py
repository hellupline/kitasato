from kitasato import tree, response


class Index(response.RenderMixin, tree.EndpointHandler):
    show_in_menu = True
    name = 'Index'
    url = '/index'
    endpoint = 'index'

    def context(self, request):
        return {'data': {}}


class Create(response.RenderMixin, tree.EndpointHandler):
    name = 'Create'
    url = '/create'
    endpoint = 'create'

    def context(self, request):
        return {'data': {}}


class Read(response.RenderMixin, tree.EndpointHandler):
    name = 'Read'
    url = '/read/<key>'
    endpoint = 'read'

    def context(self, request, key):
        return {'data': {'key': key}}


class Update(response.RenderMixin, tree.EndpointHandler):
    name = 'Update'
    url = '/update/<key>'
    endpoint = 'update'

    def context(self, request, key):
        return {'data': {'key': key}}


class Delete(response.RenderMixin, tree.EndpointHandler):
    name = 'Delete'
    url = '/delete/<key>'
    endpoint = 'delete'

    def context(self, request, key):
        return {'data': {'key': key}}

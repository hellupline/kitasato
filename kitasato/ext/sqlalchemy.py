from contextlib import contextmanager
from itertools import chain

import sqlalchemy as sa
from kitasato import resource

flatten = chain.from_iterable


class SQLAlchhemyORMController(resource.ControllerMixin):
    def __init__(self, db_session, model_class, filters=None):
        if filters is not None:
            for filter_func in filters:
                filter_func.db_session = db_session
            self.filters = filters
        self.db_session = db_session
        self.model_class = model_class

    def fetch_items(self):
        return self.db_session.query(self.model_class)

    def filter_items(self, query, filters):
        join_tables = unique(flatten(
            filter_func.join_tables
            for filter_func in self.filters.values()
        ))
        return super().filter_items(query, filters).join(join_tables)

    def sort_items(self, query, order_by, reverse=False):
        field = getattr(self.model_class, order_by)
        if reverse:
            field = -field
        query.order_by(field)

    def slice_items(self, query, page=1):
        start = (page-1)*self.per_page
        return query.offset(start).limit(self.per_page)

    def count_items(self, query):
        stmt = query.statement.with_only_columns([sa.func.count()])
        return self.db_session.execute(stmt).scalar()

    def create_item(self, data):
        item = self.new_obj()
        return self.update_item(item, data)

    def get_item(self, pk):
        return self.fetch_items().get(pk)

    def update_item(self, item, data):
        return self.save_obj(item)

    def delete_item(self, item):
        return self.detete_obj(item)

    def save_obj(self, item):
        with transaction(self.db_session) as session:
            session.add(item)
        return item

    def detete_obj(self, item):
        with transaction(self.db_session) as session:
            session.delete(item)

    def new_obj(self):
        return self.model_class()


class SearchFilter:
    def __init__(self, columns, join_tables=None):
        self.columns = columns
        self.join_tables = join_tables

    def filter(self, value, query):
        clauses = [column.contains(value) for column in self.columns]
        return query.filter(sa.or_(*clauses))


class FieldFilter:
    def __init__(self, column, join_tables=None):
        # I know its evil, and bad, but....
        # will inject session in SQLAlchhemyORMController.__init__
        self.db_session = None
        self.column = column
        self.join_tables = join_tables

    def filter(self, value, query):
        return query.filter(self.column == value)

    def get_choices(self):
        values = self.db_session.query(self.column).distinct()
        for value in chain.from_iterable(values):
            title = str(value).capitalize()
            if isinstance(value, bool):
                value = str(int(value))
            yield value, title


@contextmanager
def transaction(db_session):
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise


def unique(items):
    done = set()
    for item in items:
        if item in done:
            continue
        done.add(item)
        yield item

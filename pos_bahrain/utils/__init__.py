from functools import partial
from toolz import keyfilter, compose, curry, reduceby, merge, concatv,excepts
from pymysql.err import ProgrammingError


def pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)


@curry
def sum_by(key, iterand):
    return compose(sum, partial(map, lambda x: x.get(key) or 0))(iterand)


def with_report_error_check(data_fn):
    def fn(*args, **kwargs):
        try:
            return data_fn(*args, **kwargs)
        except ProgrammingError:
            return []

    return fn


def key_by(key, items):
    return reduceby(key, lambda a, x: merge(a, x), items, {})

split_to_list = excepts(
    AttributeError,
    compose(
        list,
        partial(filter, lambda x: x),
        partial(map, lambda x: x.strip()),
        lambda x: x.split(","),
    ),
    lambda x: None,
)

mapf = compose(list, map)
filterf = compose(list, filter)
concatvf = compose(list, concatv)
map_resolved = mapf

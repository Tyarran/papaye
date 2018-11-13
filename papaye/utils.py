def filter_set(condition, iterable, key, value):
    for item in iterable:
        if condition(item):
            item[key] = value
        yield item

from functools import wraps
from collections import defaultdict


class StateManager(object):

    def __init__(self):
        self.route_mapping = defaultdict(dict)

    def router(self, identifier, factory):
        self.factory = factory

        def decorator(path):

            def wrapped(func):
                self.route_mapping[identifier][path] = func
                return func
            return wrapped
        return decorator

    def __call__(self, identifier):

        def wrapper(func):

            @wraps(func)
            def wrapped(context, request, *args, **kwargs):
                path = f"/{'/'.join(request.matchdict['path'])}"
                ssr_view = self.route_mapping[identifier].get(path)
                state = self.factory(context, request, *args, **kwargs)
                if ssr_view:
                    state = ssr_view(context, request, state)
                return func(context, request,  state=state, **kwargs)
            return wrapped
        return wrapper


state_manager = StateManager()

import re
import types

from collections import OrderedDict, defaultdict
from functools import wraps


class RouteResolver(object):
    def __init__(self, route_mapping):
        self.route_mapping = route_mapping

    def pattern_info(self, path_part):
        if not path_part.startswith(":"):
            return {"name": None, "value": path_part}
        elif path_part[-1] == "*":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "*"}
        elif path_part[-1] == "?":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "?"}
        elif path_part[-1] == "+":
            return {"name": path_part[1:-1], "value": path_part, "quantifier": "+"}
        else:
            return {"name": path_part[1:], "value": path_part, "quantifier": None}

    def convert_to_regex(self, path_info):
        if not path_info["name"]:
            return f"{path_info['value']}"
        else:
            quantifier = path_info["quantifier"] or ""
            return f"(?P<{path_info['name']}>[a-zA-Z0-9\%\-\_]+){quantifier}"

    def path_to_regex(self, path):
        result = (
            self.pattern_info(pattern)
            for pattern in path.split("/")[1:]
            # if pattern != ""
        )
        converted = [self.convert_to_regex(path_info) for path_info in result]
        regex = re.compile("^\/" + "\/".join(converted) + "$")
        return regex

    def resolve(self, identifier, route_path):
        for path, (regex, view) in self.route_mapping[identifier].items():
            match = regex.match(route_path)
            if match:
                return view, match.groupdict()
        return (None, None)


class StateManager(object):
    def __init__(self):
        self.route_mapping = defaultdict(OrderedDict)
        self.route_resolver = RouteResolver(self.route_mapping)

    def router(self, identifier, factory):
        self.factory = factory

        def decorator(path):
            def wrapped(func):
                regex = self.route_resolver.path_to_regex(path)
                self.route_mapping[identifier][path] = [regex, func]
                return func

            return wrapped

        return decorator

    def __call__(self, identifier):
        def wrapper(func):
            @wraps(func)
            def wrapped(context, request, *args, **kwargs):
                add_slash = "/" if request.path.endswith("/") else ""
                path = f"/{'/'.join(request.matchdict['path'])}{add_slash}"
                ssr_view, matchdict = self.route_resolver.resolve(identifier, path)
                request.ssr_matchdict = matchdict
                state = self.factory(context, request, *args, **kwargs)
                if ssr_view:
                    if not isinstance(ssr_view, types.FunctionType):
                        state = ssr_view(context, request, state)()
                    else:
                        state = ssr_view(context, request, state)
                return func(context, request, state=state, **kwargs)

            return wrapped

        return wrapper


state_manager = StateManager()

import pkg_resources


class MergedRepository():

    def __init__(self, rrepo, lrepo, level=1, value_at_level=3):
        self.rrepo = rrepo
        self.lrepo = lrepo
        self.level = level
        self.value_at_level = value_at_level

    def _format_key(self, key):
        result = key
        if self.level == 2:
            result = key.replace('.', '-')
        if not self.level == 3:
            result = pkg_resources.safe_name(key.lower())
        return result

    def __getitem__(self, key):
        key = self._format_key(key)
        result = None

        if key not in self.keys():
            raise KeyError(key)

        if self.level != self.value_at_level:
            result = MergedRepository(
                self.rrepo.get(key, {}),
                self.lrepo.get(key, {}),
                level=self.level + 1,
                value_at_level=self.value_at_level,
            )
        else:
            result = self.lrepo[key] if key in self.lrepo else self.rrepo[key]
        return result

    def keys(self):
        return set(list(self.rrepo.keys()) + list(self.lrepo.keys()))

    def values(self):
        return set(list(self.rrepo) + list(self.lrepo))

class Context:
    def __init__(self):
        self.context = {}

    def __getitem__(self, item):
        return self.context[item]

    def __getattr__(self, item):
        return self.context.get(item)

    def update(self, other):
        self.context.update(other)


class WithContext:
    def __init__(self):
        self._context = Context()

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context.update(value)

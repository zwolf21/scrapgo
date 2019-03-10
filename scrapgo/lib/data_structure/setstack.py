from collections import UserList


class SetStack(UserList):

    def __init__(self, *args, extend_reversed=True, **kwargs):
        super().__init__(*args, **kwargs)

    def push(self, item):
        if item not in self:
            super().append(item)

    def extend(self, other):
        extends = [
            item for item in other if item not in self
        ]
        super().extend(extends[::-1] if self.extend_reversed else extends)

    def empthy(self):
        return bool(self)


# def recursive_map(seed, worker, filter=lambda w: True, **kwargs):
#     stack = SetStack([seed])
#     doneset = set()
#     while stack:
#         work = stack.pop()
#         for subwork in worker(work, **kwargs):
#             if subwork not in doneset:
#                 doneset.add(subwork)
#                 if filter(subwork):
#                     stack.push(subwork)

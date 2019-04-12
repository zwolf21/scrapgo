from collections import UserDict, namedtuple

History = namedtuple('History', ['url', 'previous', 'name'])

histories = {
    '/': History('/', None, 'root'),
    'a': History('a', '/', 'list'),
    'a/b': History('a/b', 'a', 'detail'),
    'a/b/c': History('a/b/c', 'a/b', 'detail2'),
    'a/b/c/d.gif': History('a/b/c/d.gif', 'a/b/c', 'image')
}


class HistoryDict(UserDict):

    def set_history(self, url, previous, name=None):
        if url in self:
            print('warning: {} has already exist in history'.format(url))
        self[url] = History(url, previous, name)

    def get_tracer(self, url):
        tracer = []
        previous = url
        while previous:
            try:
                p = self[previous]
                previous = p.previous
            except:
                return tracer
            else:
                if p.previous:
                    tracer.insert(0, p)
        return tracer

    def get_previous(self, url, name=None):
        history = self.get(url)
        if not history:
            return
        if name is None:
            return history.previous

        for history in self.get_tracer(url):
            if history.name == name:
                return history.url

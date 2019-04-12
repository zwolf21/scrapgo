import re
from collections import namedtuple


class BaseAction(object):

    def __init__(self, name=None, fields=None, filter=None, parser=None, static=False, refresh=False, referer=None):
        self.name = name
        self.filter = filter
        self.fields = fields
        self.parser = parser
        self.static = static
        self.refresh = refresh
        self.referer = referer
        self.urls = []


class Url(BaseAction):
    def __init__(self, url, set_params=None, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or url
        self.set_params = set_params
        self.url = url


class Root(Url):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RegexUrl(BaseAction):
    def __init__(self, regex, recursive=False, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or regex
        self.regex = re.compile(regex)
        self.recursive = recursive


class FormatUrl(BaseAction):
    def __init__(self, template, formater, **kwargs):
        super().__init__(**kwargs)
        self.name = self.name or format
        self.template = template
        self.formater = formater


def url(url, fields=None, set_params=None, name=None, filter=None, parser=None, refresh=False, relay=True, as_root=False, referer=None):
    if as_root:
        return Root(
            url,
            name=name,
            fields=fields,
            set_params=set_params,
            filter=filter,
            parser=parser,
            refresh=refresh,
            static=not relay,
            referer=referer
        )
    else:
        return Url(
            url,
            name=name,
            fields=fields,
            set_params=set_params,
            filter=filter,
            parser=parser,
            refresh=refresh,
            static=not relay,
            referer=referer
        )


def urlpattern(regx, fields=None, name=None, filter=None, parser=None, recursive=False, refresh=False, relay=True, referer=None):
    return RegexUrl(
        regx,
        name=name,
        fields=fields,
        filter=filter,
        parser=parser,
        recursive=recursive,
        refresh=refresh,
        static=not relay,
        referer=referer
    )


def urltemplate(template, renderer, fields=None, name=None, filter=None, parser=None, refresh=False, relay=True, referer=None):
    return FormatUrl(
        template,
        renderer,
        fields=fields,
        name=name,
        filter=filter,
        parser=parser,
        refresh=refresh,
        static=not relay,
        referer=referer
    )

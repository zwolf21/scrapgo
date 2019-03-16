from datetime import timedelta


# Request
USER_AGENT_NAME = 'chrome'


CACHE_NAME = 'REQUEST_CACHE'
CACHE_BACKEND = 'sqlite'
CACHE_EXPIRATION = timedelta(days=100)

# SoupParser
BEAUTIFULSOUP_PARSER = 'html.parser'
SCRAP_TARGET_ATTRS = 'href', 'src',

# pattern context field names
URLPATTERN_DISPATCHER = 'urlpattern'
REDUCER_DISPATCHER = 'reducer'
URLFILTER_DISPATCHER = 'urlfilter'
REDUCER_NAMESPACE = 'namespace'

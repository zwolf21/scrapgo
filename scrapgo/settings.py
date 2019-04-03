import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Request
USER_AGENT_NAME = 'chrome'
REQUEST_DELAY = 0.5

CACHE_NAME = 'REQUEST_CACHE'
CACHE_BACKEND = 'sqlite'
CACHE_EXPIRATION = timedelta(days=100)

# SoupParser
BEAUTIFULSOUP_PARSER = 'html.parser'
SCRAP_TARGET_ATTRS = 'href', 'src',
PARSE_CONTENT_TYPES = [
    'text/css', 'text/html', 'text/javascript', 'text/plain', 'text/xml'
]

# pattern context field names
URLPATTERN_DISPATCHER = 'urlpattern'
REDUCER_DISPATCHER = 'reducer'
URLFILTER_DISPATCHER = 'urlfilter'
REDUCER_NAMESPACE = 'namespace'

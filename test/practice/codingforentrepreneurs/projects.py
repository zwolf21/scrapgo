import os

from urllib.parse import quote, quote_plus


from scrapgo import LinkRelayScraper, url
from scrapgo.utils import urljoin, parse_src
from scrapgo.utils.fileutils import mkdir_p, cp

from .utils import encodepath, transpath
from .base import BaseScraper
from .logger import logger


class CodingForProjectsScraper(BaseScraper):
    ROOT_URL = 'https://www.codingforentrepreneurs.com/api/web/projects'
    LINK_RELAY = [
        url(
            'https://www.codingforentrepreneurs.com/api/web/projects/',
            parser='topic_parser',
            name='topic'
        ),
        url(
            'https://www.codingforentrepreneurs.com/api/web/projects/',
            generator='lecture_list_url_renderer',
            parser='lecture_list_parser',
            name='lecture_list'
        ),
        url(
            'https://www.codingforentrepreneurs.com/api/web/projects/',
            generator='lecture_url_renderer',
            parser='lecture_parser',
            name='lecture'
        )
    ]

    def topic_parser(self, response, **kwargs):
        json = response.json()

        def topic_json_parser(json):
            return [
                {
                    'topic_id': r['id'],
                    'topic_title':r['title'],
                    'topic_slug':r['slug'],
                }
                for r in json['results']
            ]
        topic_list = topic_json_parser(json)
        self.topic_list = topic_list
        return topic_list

    def lecture_list_url_renderer(self, parent_response, path, base_dir):
        for topic in self.topic_list:
            self.topic_slug = topic['topic_slug']
            path = f"{self.ROOT_URL}/{self.topic_slug}/"
            save_path = os.path.join(base_dir, 'projects', self.topic_slug)
            mkdir_p(save_path)
            yield path

    def lecture_list_parser(self, response, **kwargs):
        json = response.json()

        def lecture_list_json_parser(json):
            res = json['lectures']
            return [
                {
                    'lecture_id': r['id'],
                    'lecture_title': r['title'],
                    'lecture_slug': r['slug'],
                }
                for r in res
            ]
        lecture_list = lecture_list_json_parser(json)
        self.lecture_list = lecture_list
        return lecture_list

    def lecture_url_renderer(self, parent_response, path, **kwargs):
        for lecture in self.lecture_list:
            self.lecture_slug = lecture['lecture_slug']
            path = f"{self.ROOT_URL}/{self.topic_slug}/{self.lecture_slug}/"
            yield path

    def lecture_parser(self, response, base_dir):
        json = response.json()

        def lecture_json_parser(json):
            res = json
            return {
                'video_cdn': res['video_cdn'],
                'embed': res['embed']
            }
        lecture = lecture_json_parser(json)
        url = lecture['video_cdn'] or lecture['embed']
        if url is None:
            return lecture
        fn = parse_src(url)
        save_to = os.path.join(base_dir, 'projects', self.topic_slug, fn)
        save_to = transpath(save_to)
        url = encodepath(url)
        self._save_media(url, save_to)
        return lecture

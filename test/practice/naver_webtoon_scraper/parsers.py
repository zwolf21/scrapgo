import os
import re
from collections import namedtuple, OrderedDict

from scrapgo.utils.shortcuts import mkdir_p, cp


def _find_row(data_list, where, keyword, default=None):
    for row in data_list:
        if getattr(row, where) == keyword:
            return row
    return default


def root_parser(response, match, soup, context):
    save_to = context['save_to']
    mkdir_p(save_to)
    context[response.url] = save_to


def toon_parser(response, match, soup, context):
    titlebar = soup.title.text.split('::')
    title = titlebar[0].strip()
    titleId = match('titleId')
    weekday = match('weekday')
    author = soup.select('span.wrt_nm')[0].text.strip()

    toon_path = os.path.join(context[response.previous], title)
    mkdir_p(toon_path)
    context[response.url] = toon_path

    return {
        'toon_title': title,
        'author': author,
        'titleId': titleId,
        'weekday': weekday,
    }


def toon_thumb_parser(response, match, soup, context):
    toon_path = context[response.previous]
    path = os.path.join(toon_path, match('filename'))
    cp(path, response.content)


def episode_pagination_parser(response, match, soup, context):
    context[response.url] = context[response.previous]


def episode_thumb_parser(response, match, soup, context):
    episode_path = context[response.previous]
    EpThumb = namedtuple('EpThumb', 'titleId no filename content')
    thumb = EpThumb(
        match('titleId'), match('no'), match('filename'), response.content
    )
    context.setdefault('episode_thumb', []).append(thumb)


def episode_parser(response, match, soup, context):
    episode_title = soup.select('div.tit_area > .view > h3')[0].text.strip()
    episode_no = match('no')
    titleId = match('titleId')

    toon_path = context[response.previous]
    episode_path = os.path.join(toon_path, episode_title)
    mkdir_p(episode_path)
    context[response.url] = episode_path

    return {
        'titleId': titleId,
        'no': episode_no,
        'episode_title': episode_title,
    }


def episode_cut_parser(response, match, soup, context):
    episode_path = context[response.previous]
    path = os.path.join(episode_path, match('filename'))
    cp(path, response.content)

    titleId = match('titleId')
    no = match('no')
    episode_thumb = None
    for thumb in context['episode_thumb']:
        if thumb.titleId == titleId and thumb.no == no:
            episode_thumb = thumb
    if episode_thumb is not None:
        thumb_path = os.path.join(episode_path, episode_thumb.filename)
        cp(thumb_path, episode_thumb.content)

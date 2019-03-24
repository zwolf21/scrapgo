import os
from collections import namedtuple

from jinja2 import Environment, PackageLoader, select_autoescape
from scrapgo import settings


JINJA2_ENV = Environment(
    loader=PackageLoader('scrapgo', 'modules/output/render/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

ImageReferer = namedtuple('ImageRefer', 'src href')


def render_img2referer(save_to, image_list,
                       template_name='image2referer.html',
                       env=JINJA2_ENV):
    template = env.get_template(template_name)
    html = template.render(object_list=image_list)
    with open(save_to, 'wt', encoding='utf-8') as fp:
        fp.write(html)

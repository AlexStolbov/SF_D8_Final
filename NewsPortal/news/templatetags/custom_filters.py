from django import template
from ..resources import post_type_news, post_type_article

register = template.Library()

SWEAR_WORDS = [
    'ругань1',
    'ругань2',
    'ругань3',
]


@register.filter()
def censor(value):
    res = value

    if type(value) == str:
        for swear_word in SWEAR_WORDS:
            res = res.replace(swear_word, '****')
            res = res.replace(swear_word.capitalize(), '****')
    return res

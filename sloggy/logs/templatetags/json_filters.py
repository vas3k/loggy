# -*- coding: utf-8 -*-
import json
from django import template

register = template.Library()


@register.filter(is_safe=True)
def json_dict_items(text):
    return json.loads(text).items()

@register.filter(is_safe=True)
def json_list_items(text):
    return json.loads(text)

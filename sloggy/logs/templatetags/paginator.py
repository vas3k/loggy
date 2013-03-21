# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag("blocks/paginator.html")
def paginator(items):
    adjacent_pages = 4
    num_pages = items.paginator.num_pages
    page = items.number

    startPage = max(page - adjacent_pages, 1)
    if startPage <= 3: startPage = 1
    endPage = page + adjacent_pages + 1
    if endPage >= num_pages - 1: endPage = num_pages + 1
    page_numbers = [n for n in range(startPage, endPage) if n > 0 and n <= num_pages]

    return {
        "items": items,
        "page_numbers": page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': num_pages not in page_numbers,
        "num_pages": num_pages
    }

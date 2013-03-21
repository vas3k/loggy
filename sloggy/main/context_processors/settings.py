# -*- encoding: utf-8 -*-
from django.conf import settings

def settings_processor(request):
    return {
        "settings": settings
    }
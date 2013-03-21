# -*- encoding: utf-8 -*-
from django.conf import settings

def cookies_processor(request):
    return {
        "cookies": request.COOKIES
    }
from django.http import HttpResponse
from libs.utils import render_to


@render_to("index.html")
def index(request):
    return {}
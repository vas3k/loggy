# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

def render_to(template):
    def renderer(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            return render_to_response(tmpl, output, context_instance=RequestContext(request))
        return wrapper
    return renderer

def title(title_list=None):
    def _title(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if isinstance(output, dict):
                output.update({ "title": make_title(title_list) })
            return output
        return wrapper
    return _title

def make_title(title_list):
    if isinstance(title_list, list):
        title_string = " &larr; ".join(title_list) + "&larr;"
    elif not title_list:
        title_string = ""
    else:
        title_string = "%s &larr;" % title_list
    return title_string

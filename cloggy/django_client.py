# -*- coding: utf-8 -*-
import logging
from python_client import PythonClient, PythonLoggingHandler


class DjangoClient(PythonClient):
    def format_request(self, data):
        request = data.get("request")
        if not request:
            return {}

        result = {
            "url": request.get_full_path(),
            "host": request.get_host(),
            "method": request.method,
            "params": self._safe_jsonify_dict(request.REQUEST),
            "cookies": self._safe_jsonify_dict(request.COOKIES),
            "meta": self._safe_jsonify_dict(request.META)
        }

        return result


class DjangoLoggingHandler(PythonLoggingHandler):
    def __init__(self, level=logging.NOTSET):
        PythonLoggingHandler.__init__(self, level)
        self.client_class = DjangoClient


def loggify(project=None):
    def wrap(function):
        def wrapped(request, *args, **kwargs):
            inst = DjangoClient(module=".".join((function.__module__, function.__name__)), project=project)
            inst.catch_exception(request=request)
            return function(request, *args, **kwargs)
        return wrapped
    return wrap

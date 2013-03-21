# -*- coding: utf-8 -*-
import logging
from python_client import PythonClient, PythonLoggingHandler


class WerkzeugClient(PythonClient):
    def format_request(self, data):
        request = data.get("request")
        if not request:
            return {}

        result = {
            "url": request.full_path,
            "host": request.host,
            "method": request.method,
            "params": self._safe_jsonify_dict(request.args or request.form),
            "cookies": self._safe_jsonify_dict(request.cookies),
            "meta": self._safe_jsonify_dict(request.environ)
        }

        return result


class WerkzeugLoggingHandler(PythonLoggingHandler):
    def __init__(self, level=logging.NOTSET):
        PythonLoggingHandler.__init__(self, level)
        self.client_class = WerkzeugClient


def loggify(project=None):
    def wrap(function):
        def wrapped(request, *args, **kwargs):
            inst = WerkzeugClient(module=".".join((function.__module__, function.__name__)), project=project)
            inst.catch_exception(request=request)
            return function(request, *args, **kwargs)
        return wrapped
    return wrap

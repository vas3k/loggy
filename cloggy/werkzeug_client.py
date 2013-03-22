# -*- coding: utf-8 -*-
import logging
from python_client import PythonClient, PythonLoggingHandler


class WerkzeugClient(PythonClient):
    def __init__(self, request_provider=None, *args, **kwargs):
        self.request_provider = request_provider
        super(WerkzeugClient, self).__init__(*args, **kwargs)

    def format_request(self, data):
        request = data.get("request")
        if not request:
            if self.request_provider:
                request = self.request_provider()
        if not request:
            return {}

        result = {
            "url": getattr(request, "full_path", request.path + ("?" + request.query_string if request.query_string else "")),
            "host": request.host,
            "method": request.method,
            "params": self._safe_jsonify_dict(request.args or request.form),
            "cookies": self._safe_jsonify_dict(request.cookies),
            "meta": self._safe_jsonify_dict(request.environ)
        }

        return result


class WerkzeugLoggingHandler(PythonLoggingHandler):
    def __init__(self, level=logging.NOTSET, request_provider=None):
        PythonLoggingHandler.__init__(self, level)
        self.client_class = lambda *args, **kwargs: WerkzeugClient(request_provider=request_provider, *args, **kwargs)


def loggify(project=None):
    def wrap(function):
        def wrapped(request, *args, **kwargs):
            inst = WerkzeugClient(module=".".join((function.__module__, function.__name__)), project=project)
            inst.catch_exception(request=request)
            return function(request, *args, **kwargs)
        return wrapped
    return wrap

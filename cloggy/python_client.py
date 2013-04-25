# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import json
import sys
import platform
from cloggy_settings import *
from senders import LocalDBSender


class PythonClient(object):
    def __init__(self, module=__module__, project=DEFAULT_PROJECT_NAME, sender=LocalDBSender()):
        self.module = module
        self.project = project
        self.sender = sender

    def format_traceback(self, exc_traceback):
        """
            Формирует объект трейсбека для сохранения в БД или отправки в качестве JSON.
            Для работы требует переданного объекта-traceback, который может быть получен
            как третий возвращаемый аргумент вызова sys.exc_info()
        """
        stack = []
        while exc_traceback:
            stack.append(exc_traceback.tb_frame)
            exc_traceback = exc_traceback.tb_next

        backtrace = []
        for frame in stack:
            formatted_frame = {
                "function": frame.f_code.co_name,
                "filename": frame.f_code.co_filename,
                "line": frame.f_lineno,
                "code": "",
                "locals": {}
            }

            # вытащим код из файла
            try:
                start_line = max(0, frame.f_lineno - 7)
                end_line = start_line + 10
                with open(frame.f_code.co_filename, "r") as source_file:
                    lines = source_file.readlines()[start_line:end_line]
                formatted_frame["code"] = "".join(lines)
            except IOError:
                pass

            # вытащим локальные переменные
            local_vars = {}
            for key, value in frame.f_locals.items():
                try:
                    local_vars["%s" % key] = str(value)
                except:
                    local_vars["%s" % key] = "???"
            formatted_frame["locals"] = self._safe_jsonify_dict(local_vars)
            backtrace.append(formatted_frame)
        return backtrace

    def format_request(self, data):
        """
            По-умолчанию не знает какой вид имеет объект запроса и возвращает пустую строку.
            Метод необходимо переопределить в подклассах.
        """
        return ""

    def format_server(self, data):
        """
            Формирует название сервера
        """
        return data.get("server") or platform.node()

    def send_message(self, title, message, **kwargs):
        """
            Отправка обычного сообщения в лог. Требует заголовка и тела.
            По заголовку сообщения группируются, тело у каждого может быть различно.
            Принимает так же на вход любые дополнительные аргументы.
        """
        kwargs.update({
            "project": self.project,
            "exc_type": title,
            "exc_value": "",
            "filename": kwargs.get("filename", ""),
            "module": kwargs.get("module", self.module),
            "level": kwargs.get("level", LOG_LEVEL_DEBUG),
            "type": kwargs.get("type", LOG_TYPE_MESSAGE),
            "time": kwargs.get("time", datetime.now()),
            "content": message
        })

        try:
            kwargs.update({ "request": self.format_request(kwargs) })
        except Exception, ex:
            print "Error formatting request: %s" % ex

        try:
            kwargs.update({ "server": self.format_server(kwargs) })
        except Exception, ex:
            print "Error formatting server name: %s" % ex

        return self.sender.send(kwargs)

    def send_exception(self, exc_type, exc_value, exc_traceback, **kwargs):
        """
            Отправка исключения, принимает на вход все три возвращаемых параметра методом sys.exc_info().
            Так же принимает любые допустимые параметры в качестве kwargs.
        """
        kwargs.update({
            "project": self.project,
            "exc_type": unicode(exc_type).replace("<type '", "").replace("<class '", "").replace("'>", ""),
            "exc_value": unicode(exc_value),
            "module": kwargs.get("module", self.module),
            "level": kwargs.get("level", LOG_LEVEL_ERROR),
            "type": kwargs.get("type", LOG_TYPE_EXCEPTION),
            "time": kwargs.get("time", datetime.now()),
            "content": kwargs.get("content", "")
        })

        try:
            tb = self.format_traceback(exc_traceback)
            kwargs.update({ "traceback": tb })
            try:
                if not kwargs.get("filename"):
                    kwargs["filename"] = tb[-1]["filename"]
            except IndexError:
                kwargs["filename"] = "unknown"
        except Exception, ex:
            print "Error formatting traceback: %s" % ex

        try:
            kwargs.update({ "request": self.format_request(kwargs) })
        except Exception, ex:
            print "Error formatting request: %s" % ex

        try:
            kwargs.update({ "server": self.format_server(kwargs) })
        except Exception, ex:
            print "Error formatting server name: %s" % ex

        return self.sender.send(kwargs)

    def catch_exception(self, *args, **kwargs):
        """
            Метод-помощник для отлова исключений. Просто вызывается в блоке except и делает свое дело.
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type:
            return self.send_exception(exc_type, exc_value, exc_traceback, **kwargs)
        return None

    def _safe_jsonify_dict(self, unsafe_dict):
        if not unsafe_dict:
            return "{}"

        safe_dict = {}
        for key, value in dict(unsafe_dict).items():
            try:
                json.dumps({ key: value }, skipkeys=True)
                safe_dict.update({ key: value })
            except:
                continue

        try:
            return json.dumps(safe_dict, skipkeys=True)
        except:
            return "{}"

    def _safe_jsonify_list(self, unsafe_list):
        if not unsafe_list:
            return "{}"

        safe_list = []
        for item in list(unsafe_list):
            try:
                json.dumps(item)
                safe_list.append(item)
            except:
                continue

        try:
            return json.dumps(safe_list)
        except:
            return "[]"


class PythonLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.client_class = PythonClient

    def emit(self, record):
        client = self.client_class(module=record.module, project=DEFAULT_PROJECT_NAME)
        try:
            request = record.request
        except:
            request = None

        try:
            filename = record.pathname
        except:
            filename = None

        try:
            message = record.getMessage()
        except:
            message = None

        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            client.send_exception(
                exc_type, exc_value, exc_traceback,
                level=record.levelname.lower(),
                module="%s.%s" % (record.module, record.funcName),
                request=request,
                content=message
            )
        else:
            client.send_message(
                "%s %s" % (record.levelname, record.module),
                message,
                level=record.levelname.lower(),
                module="%s.%s" % (record.module, record.funcName),
                request=request
            )


def loggify(project=None):
    """
        Декоратор для использования там, где это удобно
    """
    def wrap(function):
        def wrapped(*args, **kwargs):
            inst = PythonClient(module=".".join((function.__module__, function.__name__)), project=project)
            inst.catch_exception()
            return function(*args, **kwargs)
        return wrapped
    return wrap


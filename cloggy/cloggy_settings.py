# -*- coding: utf-8 -*-
DB_CONNECTION_STRING = "postgresql+psycopg2://username:password@localhost/loggy"
DEFAULT_PROJECT_NAME = "default"
DB_PREFIX = ""

#

LOG_LEVEL_INFO = "info"
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVELS = (
    (LOG_LEVEL_INFO, "info"),
    (LOG_LEVEL_DEBUG, "debug"),
    (LOG_LEVEL_WARNING, "warning"),
    (LOG_LEVEL_ERROR, "error")
)

LOG_TYPE_EXCEPTION = "exception"
LOG_TYPE_MESSAGE = "message"
LOG_TYPES = (
    (LOG_TYPE_EXCEPTION, "exception"),
    (LOG_TYPE_MESSAGE, "message")
)

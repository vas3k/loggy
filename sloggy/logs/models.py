import datetime
from django.db import models
from sloggy.settings import DB_PREFIX

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


class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    full_name = models.CharField(max_length=200)
    groups_count = models.IntegerField(default=0)
    logs_count = models.IntegerField(default=0)

    class Meta:
        db_table = "%sprojects" % DB_PREFIX


class Group(models.Model):
    project = models.ForeignKey(Project, related_name="project_group")
    level = models.CharField(choices=LOG_LEVELS, max_length=20, default=LOG_LEVEL_INFO)
    type = models.CharField(choices=LOG_TYPES, max_length=20, default=LOG_TYPE_MESSAGE)
    module = models.CharField(max_length=300, blank=True, null=True)
    filename = models.CharField(max_length=500, blank=True, null=True)
    exc_name = models.CharField(max_length=800, blank=True, null=True)
    exc_value = models.CharField(max_length=800, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    logs_count = models.IntegerField(default=0)
    is_favorited = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    @staticmethod
    def request_filter(request):
        conditions = {}
        get_type = request.GET.get("type")
        if get_type:
            conditions.update({ "type": get_type })
        get_level = request.GET.get("level")
        if get_level:
            conditions.update({ "level": get_level })
        get_module = request.GET.get("module")
        if get_module:
            conditions.update({ "module": get_module })
        get_project = request.GET.get("project")
        if get_project:
            conditions.update({ "project__name": get_project })
        return Group.objects.select_related().filter(**conditions)

    class Meta:
        db_table = "%sgroups" % DB_PREFIX


class Event(models.Model):
    group = models.ForeignKey(Group, related_name="group_log")
    server = models.CharField(max_length=300, null=True)
    filename = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True)

    @staticmethod
    def request_filter(request):
        conditions = {}
        get_type = request.GET.get("type")
        if get_type:
            conditions.update({ "group__type": get_type })
        get_level = request.GET.get("level")
        if get_level:
            conditions.update({ "group__level": get_level })
        get_module = request.GET.get("module")
        if get_module:
            conditions.update({ "group__module": get_module })
        get_project = request.GET.get("project")
        if get_project:
            conditions.update({ "group__project__name": get_project })
        return Event.objects.select_related().filter(**conditions)

    class Meta:
        db_table = "%sevents" % DB_PREFIX


class Traceback(models.Model):
    event = models.ForeignKey(Event, related_name="traceback")
    filename = models.CharField(max_length=400)
    line = models.PositiveIntegerField(default=0)
    code = models.TextField(null=True)
    method = models.CharField(max_length=200)
    local_variables = models.TextField(null=True)

    class Meta:
        db_table = "%stracebacks" % DB_PREFIX


class Request(models.Model):
    event = models.OneToOneField(Event, related_name="request", blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    host = models.CharField(max_length=200, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    params = models.TextField(blank=True, null=True)
    cookies = models.TextField(blank=True, null=True)
    meta = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "%srequests" % DB_PREFIX

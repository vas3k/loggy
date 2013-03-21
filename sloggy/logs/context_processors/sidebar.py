# -*- encoding: utf-8 -*-
from django.db.models import Count
from logs.models import *


def sidebar_processor(request):
    event_types = dict([(type, { "group__type": type, "count": 0 }) for type, name in LOG_TYPES])
    for event_type in Event.objects.select_related().values("group__type").filter(group__type__isnull=False).annotate(count=Count("group__type")):
        event_types[event_type["group__type"]] = event_type

    event_levels = dict([(level, { "group__level": level, "count": 0 }) for level, name in LOG_LEVELS])
    for event_level in Event.objects.select_related().values("group__level").filter(group__level__isnull=False).annotate(count=Count("group__level")):
        event_levels[event_level["group__level"]] = event_level

    return {
        "event_types": event_types.values(),
        "event_levels": event_levels.values(),
        "event_modules": Event.objects.select_related().values("group__module").filter(group__module__isnull=False).annotate(count=Count("group__module")),
        "event_projects": Project.objects.all()
    }

# -*- coding: utf-8 -*-
from collections import defaultdict
import datetime
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from libs.utils import render_to
from models import *


def __format_graph(queryset, start_from):
    result = defaultdict(int)
    date = start_from
    while date <= datetime.datetime.now():
        result[date.date()] = 0
        date += datetime.timedelta(days=1)
    for item in queryset.order_by("created_at").filter(created_at__gte=start_from):
        result[item.created_at.date()] += 1
    return [[k.strftime("%d %b"), result[k]] for k in sorted(result)]


@render_to("group_list.html")
def group_list(request):
    paginator = Paginator(Group.request_filter(request).order_by("-updated_at"), settings.GROUPS_PER_PAGE)
    page = request.GET.get("page", 1)
    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        groups = paginator.page(1)
    except EmptyPage:
        groups = paginator.page(paginator.num_pages)

    top_graph_start_date = datetime.datetime.now() - datetime.timedelta(days=50)

    return {
        "request": request,
        "groups": groups,
        "top_graph": __format_graph(Event.request_filter(request), top_graph_start_date)
    }


@render_to("group_show.html")
def group_details(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    logs = Event.objects.filter(group_id=group_id).order_by("-created_at")
    events_graph_start_date = datetime.datetime.now() - datetime.timedelta(days=20)
    return {
        "request": request,
        "logs": logs,
        "group": group,
        "events_graph": __format_graph(
            Event.request_filter(request).filter(group_id=group_id),
            events_graph_start_date
        )
    }

@render_to("log_list.html")
def log_list(request):
    paginator = Paginator(Event.request_filter(request).order_by("-created_at"), settings.LOGS_PER_PAGE)
    page = request.GET.get("page", 1)
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)

    top_graph_start_date = datetime.datetime.now() - datetime.timedelta(days=50)

    return {
        "request": request,
        "top_graph": __format_graph(Event.request_filter(request), top_graph_start_date),
        "logs": logs
    }

@render_to("log_show.html")
def log_details(request, log_id):
    log = get_object_or_404(Event, pk=log_id)

    log_traceback = Traceback.objects.filter(event=log).order_by("-id")

    try:
        log_request = Request.objects.get(event=log)
    except:
        log_request = None

    return {
        "request": request,
        "log": log,
        "log_traceback": log_traceback,
        "log_request": log_request
    }

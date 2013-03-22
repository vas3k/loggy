# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine, func, Column, ForeignKey, Boolean, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session
from cloggy_settings import *

Base = declarative_base()

class Project(Base):
    __tablename__       = "%sprojects" % DB_PREFIX

    id                  = Column(Integer, primary_key=True)
    name                = Column(String(length=200), unique=True)
    full_name           = Column(String(length=200))
    groups_count        = Column(Integer, default=0)
    logs_count          = Column(Integer, default=0)

class Group(Base):
    __tablename__       = "%sgroups" % DB_PREFIX

    id                  = Column(Integer, primary_key=True)
    project_id          = Column(Integer, ForeignKey("%s.id" % Project.__tablename__))
    level               = Column(String(length=20), default=LOG_LEVEL_INFO)
    type                = Column(String(length=20), default=LOG_TYPE_MESSAGE)
    module              = Column(String(length=300))
    filename            = Column(String(length=500))
    exc_name            = Column(String(length=800))
    exc_value           = Column(String(length=800))
    created_at          = Column(DateTime, default=datetime.now)
    updated_at          = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    logs_count          = Column(Integer, default=0)
    is_favorited        = Column(Boolean, default=False)
    is_resolved         = Column(Boolean, default=False)

class Event(Base):
    __tablename__       = "%sevents" % DB_PREFIX

    id                  = Column(Integer, primary_key=True)
    group_id            = Column(Integer, ForeignKey("%s.id" % Group.__tablename__))
    server              = Column(String(length=200))
    filename            = Column(String(length=500))
    created_at          = Column(DateTime, default=datetime.now)
    content             = Column(Text)

class Traceback(Base):
    __tablename__       = "%stracebacks" % DB_PREFIX

    id                  = Column(Integer, primary_key=True)
    event_id            = Column(Integer, ForeignKey("%s.id" % Event.__tablename__))
    filename            = Column(String(length=400))
    line                = Column(Integer(unsigned=True))
    code                = Column(Text)
    method              = Column(String(length=200))
    local_variables     = Column(Text)

class Request(Base):
    __tablename__       =  "%srequests" % DB_PREFIX

    id                  = Column(Integer, primary_key=True)
    event_id            = Column(Integer, ForeignKey("%s.id" % Event.__tablename__))
    url                 = Column(String(length=500))
    host                = Column(String(length=200))
    method              = Column(String(length=10))
    params              = Column(Text)
    cookies             = Column(Text)
    meta                = Column(Text)

class LocalDBSender(object):
    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_STRING)

    def send(self, values):
        # get project id
        if not values.get("project"):
            values["project"] = DEFAULT_PROJECT_NAME

        session = create_session(self.engine)

        project = session.query(Project).filter(
            Project.name == values["project"]
        ).first()
        if project is None:
            project = Project()
            project.name        = values["project"]
            project.full_name   = values["project"]
            session.add(project)
            session.flush()

        group = session.query(Group).filter(
            Group.project_id    == project.id,
            Group.exc_name      == values["exc_type"],
            Group.exc_value     == values["exc_value"],
            Group.module        == values["module"],
            Group.level         == values["level"],
            Group.type          == values["type"]
        ).first()
        if group is None:
            group = Group()
            group.project_id    = project.id
            group.level         = values["level"]
            group.type          = values["type"]
            group.module        = values["module"]
            group.filename      = values["filename"]
            group.exc_name      = values["exc_type"]
            group.exc_value     = values["exc_value"]
            session.add(group)
            session.flush()

        event = Event()
        event.group_id  = group.id
        event.server    = values["server"]
        event.filename  = values["filename"]
        event.content   = values["content"]
        session.add(event)
        session.flush()

        for frame in values.get("traceback", []):
            traceback = Traceback()
            traceback.event_id          = event.id
            traceback.filename          = frame["filename"]
            traceback.line              = frame["line"]
            traceback.code              = frame["code"]
            traceback.method            = frame["function"]
            traceback.local_variables   = frame["locals"]
            session.add(traceback)

        if values.get("request"):
            request = Request()
            request.event_id    = event.id
            request.url         = values["request"]["url"]
            request.host        = values["request"]["host"]
            request.method      = values["request"]["method"]
            request.params      = values["request"]["params"]
            request.cookies     = values["request"]["cookies"]
            request.meta        = values["request"]["meta"]
            session.add(request)

        # update counters
        group.logs_count = session.query(func.count(Event.id)).filter(Event.group_id == group.id).scalar()
        project.groups_count = session.query(func.count(Group.id)).filter(Group.project_id == project.id).scalar()
        project.logs_count = session.query(func.sum(Group.logs_count)).filter(Group.project_id == project.id).scalar()

        session.flush()
        session.close()

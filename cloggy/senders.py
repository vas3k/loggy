# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine
from cloggy_settings import *

TABLE_PROJECTS = "%sprojects" % DB_PREFIX
TABLE_GROUPS = "%sgroups" % DB_PREFIX
TABLE_EVENTS = "%sevents" % DB_PREFIX
TABLE_TRACEBACKS = "%stracebacks" % DB_PREFIX
TABLE_REQUESTS = "%srequests" % DB_PREFIX


class LocalDBSender(object):
    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_STRING, echo=False)

    def send(self, values):
        values.update({
            "true": True,  # funny, hah?
            "false": False
        })

        conn = self.engine.connect()

        # get project id
        if not values.get("project"):
            values["project"] = DEFAULT_PROJECT_NAME

        projects = list(conn.execute("""
            select id, groups_count from """ + TABLE_PROJECTS + """
            where name = %(project)s
        """, values))
        if not projects:
            projects = list(conn.execute("""
                insert into """ + TABLE_PROJECTS + """ (name, full_name, logs_count, groups_count)
                values (%(project)s, %(project)s, 0, 0)
                returning id
            """, values))
        project_id = projects[0][0]
        values.update({
            "project_id": project_id
        })

        # get group id
        groups = list(conn.execute("""
            select id, logs_count from """ + TABLE_GROUPS + """
            where project_id = %(project_id)s and exc_name = %(exc_type)s and exc_value = %(exc_value)s and module = %(module)s and level = %(level)s and type = %(type)s
        """, values))
        if not groups:
            groups = list(conn.execute("""
                insert into """ + TABLE_GROUPS + """ (
                    project_id, level, type, module, filename, exc_name, exc_value,
                    created_at, updated_at, logs_count, is_favorited, is_resolved
                ) values (
                    %(project_id)s, %(level)s, %(type)s, %(module)s, %(filename)s, %(exc_type)s, %(exc_value)s,
                    %(time)s, %(time)s, 0, %(false)s, %(false)s
                ) returning id
            """, values))
        group_id = groups[0][0]
        values.update({
            "group_id": group_id
        })

        # create event
        event_id = list(conn.execute("""
            insert into """ + TABLE_EVENTS + """ (
                group_id, server, filename, created_at, content
            ) values (
                %(group_id)s, %(server)s, %(filename)s, %(time)s, %(content)s
            ) returning id
        """, values))[0][0]

        # update counters

        transaction = conn.begin()
        try:
            conn.execute("""
                update """ + TABLE_GROUPS + """
                set logs_count = (select count(*) from events where group_id = %s), updated_at = %s
                where id = %s
            """, [group_id, datetime.now(), group_id])

            conn.execute("""
                update """ + TABLE_PROJECTS + """
                set groups_count = (select count(*) from """ + TABLE_GROUPS + """ where project_id = %s),
                logs_count = (select coalesce(sum(logs_count), 1) from """ + TABLE_GROUPS + """ where project_id = %s)
                where id = %s
            """, [project_id, project_id, project_id])
            transaction.commit()
        except:
            transaction.rollback()

        print "Event id: %s" % event_id

        # save traceback
        transaction = conn.begin()
        try:
            trace = values.get("traceback")
            if trace:
                for frame in trace:
                    frame.update({
                        "event_id": event_id
                    })
                    conn.execute("""
                        insert into """ + TABLE_TRACEBACKS + """ (
                            event_id, filename, line, code, method, local_variables
                        ) values (
                            %(event_id)s, %(filename)s, %(line)s, %(code)s, %(function)s, %(locals)s
                        )
                    """, frame)
            transaction.commit()
        except:
            transaction.rollback()


        # save request
        transaction = conn.begin()
        try:
            request = values.get("request")
            if request:
                request.update({
                    "event_id": event_id
                })
                conn.execute("""
                    insert into """ + TABLE_REQUESTS + """ (
                        event_id, url, host, method, params, cookies, meta
                    ) values (
                        %(event_id)s, %(url)s, %(host)s, %(method)s, %(params)s, %(cookies)s, %(meta)s
                    )
                """, request)
            transaction.commit()
        except:
            transaction.rollback()

        conn.close()

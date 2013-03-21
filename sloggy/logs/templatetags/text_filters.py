# -*- coding: utf-8 -*-
import re
from django import template
from time import mktime, localtime

register = template.Library()

@register.filter(is_safe=True)
def escape(text):
    if text is not None:
        return text.replace(r'"', r'\"').replace(r"'", r"\'")
    else:
        return ""

@register.filter(is_safe=True)
def nl2br(text):
    text = text.replace("\n", "</p><p>")
    return text

@register.filter(is_safe=True)
def nl2br2(text):
    text = text.replace("\n", "<br />")
    return text

@register.filter(is_safe=True)
def htmlspecialchars(text):
    if text is not None:
        return text.replace(r"<", r"&lt;").replace(r">", r"&gt;")
    else:
        return ""

@register.filter(is_safe=True)
def quoting(text):
    text = text.replace(r"<", r"&lt;").replace(r">", r"&gt;")

    newtext = u""
    for line in text.split("\n"):
        if line.strip().startswith("&gt;"):
            newtext += '<span class="quote">%s</span><br />' % line
        else:
            newtext += "%s<br />" % line
    text = newtext
    text = re.sub(r"&lt;[B|b]&gt;(.*?)&lt;/[B|b]&gt;", r"<strong>\1</strong>", text)
    text = re.sub(r"&lt;[I|i]&gt;(.*?)&lt;/[I|i]&gt;", r"<i>\1</i>", text)
    text = re.sub(r"&lt;[S|s]&gt;(.*?)&lt;/[S|s]&gt;", r"<strike>\1</strike>", text)
    text = re.sub(r"&lt;[U|u]&gt;(.*?)&lt;/[U|u]&gt;", r"<u>\1</u>", text)
    text = re.sub(r"&lt;pre&gt;(.*?)&lt;/pre&gt;", r"<pre>\1</pre>", text)
    text = re.sub(r"&lt;code&gt;(.*?)&lt;/code&gt;", r"<code>\1</code>", text)
    text = re.sub(r"&lt;[hr|HR].*?/&gt;", r"<hr />", text)
    text = re.sub(u'(\(?https?://[-A-Za-zА-Яа-я0-9+&@#/%?=~_()|!:,.;]*[-A-Za-zА-Яа-я0-9+&@#/%=~_()|])(\">|</a>)?', r'<a href="\1">\1</a>', text)
    text = re.sub(r'&lt;[a|A] href=["|\']<a href="(.*?)">.*?</a>["|\']&gt;(.*?)&lt;/[A|a]&gt;', r'<a href="\1">\2</a>', text)
    #text = nl2br2(text)
    return text

@register.filter
def rupluralize(value, arg="дурак,дурака,дураков"):
    args = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]

@register.filter
def relative_date(value):
    then = int(mktime(value.timetuple()))
    now = int(mktime(localtime()))
    seconds = now - then

    hours = seconds / 3600
    minutes = (seconds % 3600) / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = months / 12

    if years > 0:
        if years > 1:
            return u"около %s %s назад" % (years, rupluralize(years, u"года,лет,лет"))
        return u"около года назад"
    if months > 0:
        if months > 1:
            return u"около %s %s назад" % (months, rupluralize(months, u"месяца,месяцев,месяцев"))
        return u"около месяца назад"
    if weeks > 0:
        if weeks > 1:
            return u"%s %s назад" % (weeks, rupluralize(weeks, u"неделю,недели,недель"))
        return u"на этой неделе"
    if days > 0:
        if days > 1:
            return u"%s %s назад" % (days, rupluralize(days, u"день,дня,дней"))
        return u"вчера"
    if hours > 0:
        if hours > 1:
            return u"%s %s назад" % (hours, rupluralize(hours, u"час,часа,часов"))
        return u"час назад"
    if minutes > 0:
        if minutes > 1:
            return u"%s %s назад" % (minutes, rupluralize(minutes, u"минуту,минуты,минут"))
        return u"минуту назад"
    return u"только что"

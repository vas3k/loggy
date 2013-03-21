# -*- coding: utf-8 -*-
from django import template
register = template.Library()

class MagicParams(template.Node):
    def __init__(self, get, key, value, url):
        self.var_get = template.Variable(get)
        self.var_key = template.Variable(key)
        self.var_value = template.Variable(value)
        self.var_url = template.Variable(url)

    def render(self, context):
        try:
            get = self.var_get.resolve(context)
            key = self.var_key.resolve(context)
            value = self.var_value.resolve(context)
            url = self.var_url.resolve(context)
        except template.VariableDoesNotExist:
            return "/"

        params = dict([(k, v) for k, v in get.items()])
        if value:
            params.update({ key: value })
        else:
            if key in params.keys():
                del params[key]

        if params:
            return "%s?" % url + "&".join(["%s=%s" % (k, v) for k, v in params.items()])
        else:
            return "%s" % url


@register.tag
def magic_params(parser, token):
    try:
        tag_name, request_get, key, value, url = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires four arguments" % token.contents.split()[0])

    return MagicParams(request_get, key, value, url)



from django import template

register = template.Library()


@register.filter
def get_unique(value, arg):
    return list(map(lambda x: x[arg], list(value.values(arg).distinct(arg))))


register.filter("get_unique", get_unique)

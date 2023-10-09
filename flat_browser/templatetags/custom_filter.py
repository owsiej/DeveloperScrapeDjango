from django import template

register = template.Library()


@register.filter
def get_unique(value, arg):
    lista = set(map(lambda x: x[arg], list(value.values(arg))))
    return list(lista)


register.filter("get_unique", get_unique)

from django import template

register = template.Library()

@register.filter
def access(value, arg):
    print("value")
    print(value)
    print("arg")
    print(arg)
    return value[arg]

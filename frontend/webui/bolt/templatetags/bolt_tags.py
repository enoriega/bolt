from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def filter_refhyp(value):
    '''Filters a ref/hyp string and returns the human friendly representation'''   
    return value.lower().replace('*', '')


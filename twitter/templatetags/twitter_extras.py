from django import template
from datetime import datetime

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

@register.filter
def month_year(date: datetime) -> str:
    """returns month-year of given date"""
    if type(date) != datetime:
        return ""
    return date.strftime('%m-%Y')

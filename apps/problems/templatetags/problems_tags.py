from django import template

import markdown

# execution status
from libs.code.status import execution_status_msg

register=template.Library()
# USELESS
def description_to_html(description_str):
    return markdown.markdown(description_str)

# USELESS
def has_permission(user, arg1, arg2=None):
    print(user, arg1, arg2)
    if user.is_superuser:
        return True
    if arg1=="edit_datafile":
        
        return 
    return False

def translate_status(status):
    if status==0:
        return "SUCCESS"
    return execution_status_msg[status]
    return "FAILURE"
# register tags
register.filter("description_to_html", description_to_html)
register.filter("has_permission",has_permission)
register.filter("translate_status", translate_status)

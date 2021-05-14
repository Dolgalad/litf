from django import template

import markdown

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

# register tags
register.filter("description_to_html", description_to_html)
register.filter("has_permission",has_permission)

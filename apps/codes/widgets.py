"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Some custom widgets
"""
from django.forms import Select
class CodeSelectionWidget(Select):
    template_name="codes/widgets/code_selection_widget.html"
    #template_name="django/forms/widgets/select.html"
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
    def render(self, name, value, attrs={}, renderer=None):
        a=super().render(name, value, attrs, renderer)
        return a

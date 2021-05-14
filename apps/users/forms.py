from django import forms
from django.core.exceptions import ValidationError
class LoginForm(forms.Form):
    username=forms.CharField(required=False)
    password=forms.CharField(widget=forms.PasswordInput, required=False)
    def clean(self):
        cleaned_data=super().clean()
    def is_valid(self):
        print("In LoginForm.is_valid()")
        return super().is_valid()

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
class RegistrationForm(forms.Form):
    username=forms.CharField(label="Username", max_length=100)
    email=forms.EmailField()
    password=forms.CharField(max_length=32, widget=forms.PasswordInput)
    password_confirm=forms.CharField(max_length=32, widget=forms.PasswordInput)
    def clean(self):
        cleaned_data=super().clean()
        print("in RegistrationForm clean : {}".format(cleaned_data))
        # check if user exists
        u=cleaned_data.get("username")
        p,pc=cleaned_data.get("password"),cleaned_data.get("password_confirm")
        validate_password(p,user=u)
        if u:
            if self.username_exists(u):
                raise ValidationError("Username {} already exists".format(u))
            if not self.check_password(p,pc):
                raise ValidationError("Password and confirmation do not match")
    def username_exists(self, u):
        print("Checking username : {}".format(u))
        try:
            username_exists=User.objects.get(username=u) is not None
            print("User exists : {}".format(username_exists))
            return True
        except:
            pass
        return False
    def check_password(self, pwd, pwd_conf):
        return pwd==pwd_conf




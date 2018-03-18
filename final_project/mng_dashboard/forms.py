from django import forms
from .models import Employee, TimeExp, TIME_EXP_TYPES
from django.contrib.auth.models import User


class LogInForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }



class NewEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            "active": forms.HiddenInput
        }
        verbose_name = {
            "int_id": "SAP ID",
        }
        help_texts = {
            "email": "Remember! Email address has to end with domain @emp_mail.com"
        }


class TimeExpForm(forms.Form):
    clerk = forms.IntegerField(label = "Clerk's ID", widget= forms.HiddenInput)
    type = forms.ChoiceField(choices=TIME_EXP_TYPES)
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))




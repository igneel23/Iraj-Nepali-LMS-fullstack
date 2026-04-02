from django import forms
from .models import StudentProfile

class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    username = forms.CharField(max_length=50, required=False, disabled=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = StudentProfile
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'date_of_birth',
            'phone_number',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
        }

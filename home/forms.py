from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class SignupForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, required=True, label="Full Name")
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['full_name'].split(' ')[0],
            last_name=' '.join(self.cleaned_data['full_name'].split(' ')[1:]) if len(self.cleaned_data['full_name'].split(' ')) > 1 else ''
        )
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ClientProfile, Transaction, AgentProfile


class LoginForm(forms.Form):
    identifier = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email or Username'}),
        label="Email or Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password"
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        required=True
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ('first_name', 'last_name', 'phone_number', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


class TransactionForm(forms.ModelForm):
    agent = forms.ModelChoiceField(
        queryset=AgentProfile.objects.none(),
        required=False,
        label='Choose an online agent',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Transaction
        fields = ('platform', 'currency', 'amount', 'payment_method', 'payment_phone')
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number for Payment'}),
        }

    def __init__(self, *args, **kwargs):
        active_agents = kwargs.pop('active_agents', AgentProfile.objects.filter(is_online=True))
        super().__init__(*args, **kwargs)
        field = self.fields['agent']
        field.queryset = active_agents
        field.empty_label = 'Select an agent'
        if active_agents.exists():
            field.required = True
        else:
            field.widget = forms.HiddenInput()

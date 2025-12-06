from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ClientProfile, Transaction, AgentProfile, AgentApplication, PricingSettings


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


class AgentApplicationForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    crypto_addresses = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    compliance_experience = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    additional_notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)

    class Meta:
        model = AgentApplication
        fields = [
            'full_name','email','phone_number','country','city','id_type','id_number','date_of_birth',
            'years_of_experience','platforms_supported','fiat_payout_methods','crypto_addresses',
            'daily_liquidity_capacity','compliance_experience','has_aml_policy','accepts_background_check',
            'terms_acknowledged','additional_notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'id_type': forms.Select(attrs={'class': 'form-select'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'platforms_supported': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Binance, Bybit, ...'}),
            'fiat_payout_methods': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M-Pesa, Bank wires'}),
            'daily_liquidity_capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'has_aml_policy': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'accepts_background_check': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'terms_acknowledged': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PricingSettingsForm(forms.ModelForm):
    class Meta:
        model = PricingSettings
        fields = ['exchange_rate', 'transaction_fee_percent']
        widgets = {
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transaction_fee_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

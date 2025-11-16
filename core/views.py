
from django.shortcuts import render, redirect
from .forms import LoginForm, forms

def landing(request):
    return render(request, 'landing.html')



def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Placeholder: handle authentication here
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        # You can use Django auth later
        return redirect('landing')  # Redirect after login

    return render(request,'login.html', {'form': form})

# Simple signup form
class SignUpForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

def signup_view(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Placeholder: save user or integrate Django auth here
        return redirect('landing')  # Redirect after signup
    return render(request, 'auth/signup.html', {'form': form})


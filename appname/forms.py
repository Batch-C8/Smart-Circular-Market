from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser 
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=30,required=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

class ResetPasswordForm(forms.Form):
    email = forms.EmailField()
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

class ManualForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your username"}))
    vehicle_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter vehicle name"}))
    model_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter model name"}))
    manufacturer_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter manufacturer name"}))
    manufacturing_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    product_condition = forms.ChoiceField(choices=[("good", "Good"), ("average", "Average"), ("bad", "Bad"), ("worst", "Worst")], widget=forms.Select(attrs={"class": "form-control"}))
    product_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    product_video = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    kilometers_driven = forms.IntegerField(min_value=0, label="Kilometers Driven")

class BillForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your username"}))
    bill_image = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    product_condition = forms.ChoiceField(choices=[("good", "Good"), ("average", "Average"), ("bad", "Bad"), ("worst", "Worst")], widget=forms.Select(attrs={"class": "form-control"}))
    product_image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    product_video = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))

from django import forms
from .models import Product, Category, Supplier

from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'is_superuser', 
            'password', 
            'username', 
            'email', 
            'first_name', 
            'last_name',
            'is_active',
            'is_staff',
            'date_joined'
        ]
        widgets = {
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "date_joined": forms.DateTimeInput(attrs={"class": "form-control"}),
        }
class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by('name'),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Categoria"
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.order_by('name'),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Fornecedor"
    )

    class Meta:
        model = Product
        fields = [
            'name', 
            'description', 
            'price', 
            'stock', 
            'url_image',
            'category',
            'supplier'
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}
            ),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "url_image": forms.URLInput(attrs={"class": "form-control"}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
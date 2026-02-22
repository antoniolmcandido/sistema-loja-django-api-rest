from django import forms
from django.contrib.auth.models import User


class UserForm(forms.Form):
    """Formulário para criar usuários - ainda usa o modelo direto (necessário)"""

    username = forms.CharField(
        max_length=150,
        label="Usuário",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    is_staff = forms.BooleanField(
        label="É Staff?",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def save(self):
        """Cria o usuário no banco"""
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_staff=self.cleaned_data["is_staff"],
        )
        return user


class ProductForm(forms.Form):
    """✅ Formulário genérico - SEM dependência do modelo Product"""

    name = forms.CharField(
        max_length=100,
        label="Nome",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Preço",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    stock = forms.IntegerField(
        label="Estoque", widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    category = forms.IntegerField(
        label="Categoria", widget=forms.Select(attrs={"class": "form-control"})
    )
    supplier = forms.IntegerField(
        label="Fornecedor", widget=forms.Select(attrs={"class": "form-control"})
    )
    url_image = forms.URLField(
        label="URL da Imagem",
        required=False,
        widget=forms.URLInput(attrs={"class": "form-control"}),
    )


class CategoryForm(forms.Form):
    """✅ Formulário genérico - SEM dependência do modelo Category"""

    name = forms.CharField(
        max_length=100,
        label="Nome",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        label="Descrição",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )


class SupplierForm(forms.Form):
    """✅ Formulário genérico - SEM dependência do modelo Supplier"""

    name = forms.CharField(
        max_length=100,
        label="Nome",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    contact_email = forms.EmailField(
        label="Email de Contato",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        max_length=20,
        label="Telefone",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    address = forms.CharField(
        label="Endereço",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

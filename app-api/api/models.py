from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(verbose_name='Descrição')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Preço',
        validators=[
            MinValueValidator(Decimal('0.01')), 
        ]
    )
    stock = models.PositiveIntegerField(verbose_name='Estoque')
    url_image = models.URLField(max_length=200, blank=True, verbose_name='URL da Imagem')

    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        verbose_name='Categoria',
    )
    supplier = models.ForeignKey(
        "Supplier",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        verbose_name='Fornecedor',
    )

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nome')
    description = models.TextField(verbose_name='Descrição')

    def __str__(self):
        return self.name
    
class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    contact_email = models.EmailField(verbose_name='Email de Contato')
    phone = models.CharField(max_length=15, verbose_name='Telefone')
    address = models.CharField(max_length=200, verbose_name='Endereço')

    def __str__(self):
        return self.name
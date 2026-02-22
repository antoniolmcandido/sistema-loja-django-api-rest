from django.contrib import admin
from .models import Product, Category, Supplier

# Register your models here.
# admin.site.register(Product)
# admin.site.register(Category)
# admin.site.register(Supplier)

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category", "supplier")
    search_fields = ("name", "category__name", "supplier__name")
    list_filter = ("category", "supplier")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone")
    search_fields = ("name", "contact_email", "phone")
    list_filter = ("name",)

if admin.site is not None:
    admin.site.register(Product, ProductAdmin)
    admin.site.register(Category, CategoryAdmin)
    admin.site.register(Supplier, SupplierAdmin)
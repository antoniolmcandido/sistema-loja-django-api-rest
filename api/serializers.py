from rest_framework import serializers
from shop.models import Category, Supplier, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    # Passar todos os dados da categoria e fornecedor relacionados
    # category = CategorySerializer(read_only=True)
    # supplier = SupplierSerializer(read_only=True)

    # Adicionar campos somente leitura para os nomes da categoria e fornecedor
    # category_name = serializers.ReadOnlyField(source='category.name')
    # supplier_name = serializers.ReadOnlyField(source='supplier.name')

    class Meta:
        model = Product
        fields = "__all__"
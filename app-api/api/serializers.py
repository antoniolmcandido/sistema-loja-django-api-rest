from rest_framework import serializers
from .models import Category, Supplier, Product
from django.contrib.auth.models import User

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

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ['id', 'date_joined']
    
    def create(self, validated_data):
        """Cria um usuário com senha criptografada."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False),
            is_active=validated_data.get('is_active', True)
        )
        return user
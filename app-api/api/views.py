from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Supplier, Product
from .serializers import CategorySerializer, SupplierSerializer, ProductSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .permissions import IsStaffUser

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Configuração dos Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Campos filtrados
    filterset_fields = ['category', 'supplier']

    # Campos pesquisados
    search_fields = ['name', 'description']

    # Campos para ordenação
    ordering_fields = ['price', 'name', 'stock']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Retorna dados do usuário autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def validate_token(self, request):
        """Valida se o token é válido e retorna dados do usuário."""
        return Response({
            'valid': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'is_staff': request.user.is_staff,
                'is_authenticated': request.user.is_authenticated
            }
        })
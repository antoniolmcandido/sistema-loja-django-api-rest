from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, SupplierViewSet, ProductViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Imports do Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API da Loja Django",
        default_version="v1",
        description="API para gestão de produtos, categorias e fornecedores.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@loja.local"),
        license=openapi.License(name="MTI License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"suppliers", SupplierViewSet)
router.register(r"products", ProductViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Rotas de autenticação JWT
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Rotas do Swagger
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
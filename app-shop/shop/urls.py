from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path("create_product/", views.product_create, name="product_create"),
    path("create_category/", views.category_create, name="category_create"),
    path("create_supplier/", views.supplier_create, name="supplier_create"),
    path("create_user/", views.user_create, name="user_create"),
    path("edit_product/<int:pk>/", views.product_update, name="product_update"),
    path("delete_product/<int:pk>/", views.product_delete, name="product_delete"),
]

handler404 = "shop.views.custom_page_not_found_view"
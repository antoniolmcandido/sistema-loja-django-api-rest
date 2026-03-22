"""
Testes Automatizados para a API da Loja
Arquivo: app-tests.py

Este arquivo contém testes para:
- Modelos (Category, Supplier, Product)
- Endpoints da API (GET, POST, PUT, DELETE)
- Autenticação JWT
- Permissões
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Category, Supplier, Product
from datetime import datetime

# ============================================================================
# TESTES DE MODELOS (UNIT TESTS)
# ============================================================================

class CategoryModelTest(TestCase):
    """Testes unitários para o modelo Category"""

    def setUp(self):
        """Executado antes de cada teste"""
        self.category = Category.objects.create(
            name="Eletrônicos",
            description="Produtos eletrônicos diversos"
        )

    def test_category_creation(self):
        """Testa se a categoria foi criada corretamente"""
        self.assertEqual(self.category.name, "Eletrônicos")
        self.assertEqual(self.category.description, "Produtos eletrônicos diversos")

    def test_category_str_method(self):
        """Testa o método __str__ da categoria"""
        self.assertEqual(str(self.category), "Eletrônicos")

    def test_category_can_be_updated(self):
        """Testa se a categoria pode ser atualizada"""
        self.category.name = "Informática"
        self.category.save()
        updated_category = Category.objects.get(id=self.category.id)
        self.assertEqual(updated_category.name, "Informática")

    def test_category_can_be_deleted(self):
        """Testa se a categoria pode ser deletada"""
        category_id = self.category.id
        self.category.delete()
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=category_id)


class SupplierModelTest(TestCase):
    """Testes unitários para o modelo Supplier"""

    def setUp(self):
        """Executado antes de cada teste"""
        self.supplier = Supplier.objects.create(
            name="Fornecedor Tech",
            contact_email="contato@fornecedor.com",
            phone="11999999999",
            address="Rua Teste, 123"
        )

    def test_supplier_creation(self):
        """Testa se o fornecedor foi criado corretamente"""
        self.assertEqual(self.supplier.name, "Fornecedor Tech")
        self.assertEqual(self.supplier.contact_email, "contato@fornecedor.com")
        self.assertEqual(self.supplier.phone, "11999999999")

    def test_supplier_str_method(self):
        """Testa o método __str__ do fornecedor"""
        self.assertEqual(str(self.supplier), "Fornecedor Tech")

    def test_supplier_email_validation(self):
        """Testa se o email do fornecedor é válido"""
        self.assertIn("@", self.supplier.contact_email)


class ProductModelTest(TestCase):
    """Testes unitários para o modelo Product"""

    def setUp(self):
        """Executado antes de cada teste"""
        self.category = Category.objects.create(
            name="Informática",
            description="Produtos de informática"
        )
        self.supplier = Supplier.objects.create(
            name="Distribuidor A",
            contact_email="vendas@distribuidor.com",
            phone="11988888888",
            address="Av. Principal, 456"
        )
        self.product = Product.objects.create(
            name="Notebook Dell",
            description="Notebook para trabalho",
            price=Decimal("3500.00"),
            stock=10,
            url_image="https://m.media-amazon.com/images/I/51BUvJmmFAL._AC_SY450_.jpg",
            category=self.category,
            supplier=self.supplier
        )

    def test_product_creation(self):
        """Testa se o produto foi criado corretamente"""
        self.assertEqual(self.product.name, "Notebook Dell")
        self.assertEqual(self.product.price, Decimal("3500.00"))
        self.assertEqual(self.product.stock, 10)

    def test_product_str_method(self):
        """Testa o método __str__ do produto"""
        self.assertEqual(str(self.product), "Notebook Dell")

    def test_product_relationships(self):
        """Testa os relacionamentos do produto"""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.supplier, self.supplier)

    def test_product_category_cascade_delete(self):
        """Testa se ao deletar a categoria, o produto também é deletado"""
        product_id = self.product.id
        self.category.delete()
        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=product_id)

    def test_product_price_is_decimal(self):
        """Testa se o preço é um Decimal"""
        self.assertIsInstance(self.product.price, Decimal)


# ============================================================================
# TESTES DE API - AUTENTICAÇÃO
# ============================================================================

class AuthenticationAPITest(APITestCase):
    """Testes para autenticação JWT"""

    def setUp(self):
        """Cria usuário para testes"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.token_url = '/auth/token/'

    def test_obtain_jwt_token_with_valid_credentials(self):
        """Testa obtenção de token com credenciais válidas"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_jwt_token_with_invalid_credentials(self):
        """Testa obtenção de token com credenciais inválidas"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.token_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_without_token(self):
        """Testa acesso a endpoint protegido sem token"""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ============================================================================
# TESTES DE API - CATEGORIAS
# ============================================================================

class CategoryAPITest(APITestCase):
    """Testes para endpoints de Category"""

    def setUp(self):
        """Prepara dados para cada teste"""
        # Cria usuário e obtém token
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',       
            is_superuser= 1,
            first_name="",
            last_name="",
            email= "test@admin.com",
            is_staff= 1,
            is_active= 1,
            date_joined=datetime.strptime('2025-12-21 18:40:47 -0300', '%Y-%m-%d %H:%M:%S %z')
        )
        response = self.client.post('/auth/token/', {
            'username': 'apiuser',
            'password': 'apipass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Cria categoria de teste
        self.category = Category.objects.create(
            name="Eletrônicos",
            description="Produtos eletrônicos"
        )

    def test_list_categories(self):
        """Testa listagem de categorias (GET)"""
        response = self.client.get('/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Eletrônicos")

    def test_retrieve_category(self):
        """Testa buscar uma categoria específica (GET)"""
        response = self.client.get(f'/categories/{self.category.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Eletrônicos")

    def test_create_category(self):
        """Testa criação de categoria (POST)"""
        data = {
            'name': 'Livros',
            'description': 'Livros diversos'
        }
        response = self.client.post('/categories/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Livros')

    def test_create_category_without_name(self):
        """Testa criação de categoria sem nome (deve falhar)"""
        data = {
            'description': 'Descrição sem nome'
        }
        response = self.client.post('/categories/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category(self):
        """Testa atualização de categoria (PUT)"""
        data = {
            'name': 'Informática',
            'description': 'Produtos de informática e computação'
        }
        response = self.client.put(
            f'/categories/{self.category.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Informática')

    def test_partial_update_category(self):
        """Testa atualização parcial de categoria (PATCH)"""
        data = {'name': 'Eletrônicos e Games'}
        response = self.client.patch(
            f'/categories/{self.category.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Eletrônicos e Games')

    def test_delete_category(self):
        """Testa deleção de categoria (DELETE)"""
        response = self.client.delete(f'/categories/{self.category.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)


# ============================================================================
# TESTES DE API - FORNECEDORES
# ============================================================================

class SupplierAPITest(APITestCase):
    """Testes para endpoints de Supplier"""

    def setUp(self):
        """Prepara dados para cada teste"""
        # Autenticação
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',       
            is_superuser= 1,
            first_name="",
            last_name="",
            email= "test@admin.com",
            is_staff= 1,
            is_active= 1,
            date_joined=datetime.strptime('2025-12-21 18:40:47 -0300', '%Y-%m-%d %H:%M:%S %z')
        )
        response = self.client.post('/auth/token/', {
            'username': 'apiuser',
            'password': 'apipass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Cria fornecedor de teste
        self.supplier = Supplier.objects.create(
            name="Fornecedor XYZ",
            contact_email="xyz@example.com",
            phone="11987654321",
            address="Rua ABC, 789"
        )

    def test_list_suppliers(self):
        """Testa listagem de fornecedores (GET)"""
        response = self.client.get('/suppliers/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_supplier(self):
        """Testa criação de fornecedor (POST)"""
        data = {
            'name': 'Novo Fornecedor',
            'contact_email': 'novo@fornecedor.com',
            'phone': '11999887766',
            'address': 'Av. Nova, 100'
        }
        response = self.client.post('/suppliers/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Novo Fornecedor')

    def test_create_supplier_with_invalid_email(self):
        """Testa criação de fornecedor com email inválido"""
        data = {
            'name': 'Fornecedor Teste',
            'contact_email': 'email-invalido',  # Email sem @
            'phone': '11999887766',
            'address': 'Rua Teste, 200'
        }
        response = self.client.post('/suppliers/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_supplier(self):
        """Testa atualização de fornecedor (PUT)"""
        data = {
            'name': 'Fornecedor Atualizado',
            'contact_email': 'atualizado@example.com',
            'phone': '11999999999',
            'address': 'Nova Rua, 999'
        }
        response = self.client.put(
            f'/suppliers/{self.supplier.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Fornecedor Atualizado')

    def test_delete_supplier(self):
        """Testa deleção de fornecedor (DELETE)"""
        response = self.client.delete(f'/suppliers/{self.supplier.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.count(), 0)


# ============================================================================
# TESTES DE API - PRODUTOS
# ============================================================================

class ProductAPITest(APITestCase):
    """Testes para endpoints de Product"""

    def setUp(self):
        """Prepara dados para cada teste"""
        # Autenticação
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',       
            is_superuser= 1,
            first_name="",
            last_name="",
            email= "test@admin.com",
            is_staff= 1,
            is_active= 1,
            date_joined=datetime.strptime('2025-12-21 18:40:47 -0300', '%Y-%m-%d %H:%M:%S %z')
        )
        response = self.client.post('/auth/token/', {
            'username': 'apiuser',
            'password': 'apipass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Cria dados relacionados
        self.category = Category.objects.create(
            name="Tecnologia",
            description="Produtos tecnológicos"
        )
        self.supplier = Supplier.objects.create(
            name="Tech Supplier",
            contact_email="tech@supplier.com",
            phone="11988887777",
            address="Tech Street, 100"
        )

        # Cria produto de teste
        self.product = Product.objects.create(
            name="Mouse Gamer",
            description="Mouse com RGB",
            price=Decimal("150.00"),
            stock=50,
            url_image="https://m.media-amazon.com/images/I/61WrR7z-pGL._AC_SY450_.jpg",
            category=self.category,
            supplier=self.supplier
        )

    def test_list_products(self):
        """Testa listagem de produtos (GET)"""
        response = self.client.get('/products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Mouse Gamer")

    def test_retrieve_product(self):
        """Testa buscar um produto específico (GET)"""
        response = self.client.get(f'/products/{self.product.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Mouse Gamer")
        self.assertEqual(float(response.data['price']), 150.00)

    def test_create_product(self):
        """Testa criação de produto (POST)"""
        data = {
            'name': 'Teclado Mecânico',
            'description': 'Teclado RGB',
            'price': '250.00',
            'stock': 30,
            'url_image': 'https://m.media-amazon.com/images/I/61Tn5a431IL._AC_SX450_.jpg',
            'category': self.category.id,
            'supplier': self.supplier.id
        }
        response = self.client.post('/products/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Teclado Mecânico')

    def test_create_product_with_negative_price(self):
        """Testa criação de produto com preço negativo (deve falhar)"""
        data = {
            'name': 'Produto Inválido',
            'description': 'Teste',
            'price': '-100.00',
            'stock': 10,
            'category': self.category.id,
            'supplier': self.supplier.id
        }
        response = self.client.post('/products/', data)

        # Preço negativo deve ser rejeitado
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_product_stock(self):
        """Testa atualização de estoque de produto (PATCH)"""
        data = {'stock': 100}
        response = self.client.patch(
            f'/products/{self.product.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 100)

    def test_delete_product(self):
        """Testa deleção de produto (DELETE)"""
        response = self.client.delete(f'/products/{self.product.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_filter_products_by_category(self):
        """Testa filtro de produtos por categoria"""
        response = self.client.get(
            f'/products/?category={self.category.id}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_products_by_name(self):
        """Testa busca de produtos por nome"""
        response = self.client.get('/products/?search=Mouse')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


# ============================================================================
# TESTES DE API - USUÁRIOS E PERMISSÕES
# ============================================================================

class UserAPITest(APITestCase):
    """Testes para endpoints de User"""

    def setUp(self):
        """Prepara dados para cada teste"""
        # Cria usuário staff (admin)
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        # Cria usuário comum
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )

    def test_staff_user_can_access_users_endpoint(self):
        """Testa se usuário staff pode acessar lista de usuários"""
        # Faz login como admin
        response = self.client.post('/auth/token/', {
            'username': 'admin',
            'password': 'admin123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Acessa endpoint de usuários
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_access_users_endpoint(self):
        """Testa se usuário comum NÃO pode acessar lista de usuários"""
        # Faz login como usuário comum
        response = self.client.post('/auth/token/', {
            'username': 'regular',
            'password': 'regular123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Tenta acessar endpoint de usuários
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_access_own_data(self):
        """Testa se usuário pode acessar seus próprios dados"""
        # Faz login
        response = self.client.post('/auth/token/', {
            'username': 'regular',
            'password': 'regular123'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Acessa endpoint /me/
        response = self.client.get('/users/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'regular')


# ============================================================================
# TESTES DE INTEGRAÇÃO COMPLETOS
# ============================================================================

class IntegrationTest(APITestCase):
    """Testes que simulam fluxos completos"""

    def test_complete_product_workflow(self):
        """
        Testa fluxo completo:
        1. Criar usuário
        2. Fazer login
        3. Criar categoria
        4. Criar fornecedor
        5. Criar produto
        6. Listar produtos
        7. Atualizar produto
        8. Deletar produto
        """
        # 1. Criar usuário
        user = User.objects.create_user(
            username='workflow_user',
            password='workflow123',
        )

        # 2. Fazer login e obter token
        response = self.client.post('/auth/token/', {
            'username': 'workflow_user',
            'password': 'workflow123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # 3. Criar categoria
        category_data = {
            'name': 'Periféricos',
            'description': 'Periféricos de computador'
        }
        response = self.client.post('/categories/', category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category_id = response.data['id']

        # 4. Criar fornecedor
        supplier_data = {
            'name': 'Distribuidor Master',
            'contact_email': 'master@dist.com',
            'phone': '11987654321',
            'address': 'Rua Master, 500'
        }
        response = self.client.post('/suppliers/', supplier_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supplier_id = response.data['id']

        # 5. Criar produto
        product_data = {
            'name': 'Webcam HD',
            'description': 'Webcam 1080p',
            'price': '200.00',
            'stock': 25,
            'url_image': 'https://m.media-amazon.com/images/I/51poXd3aR4L._AC_SY300_SX300_QL70_ML2_.jpg',
            'category': category_id,
            'supplier': supplier_id
        }
        response = self.client.post('/products/', product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_id = response.data['id']

        # 6. Listar produtos
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # 7. Atualizar produto
        update_data = {'price': '180.00'}
        response = self.client.patch(
            f'/products/{product_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '180.00')

        # 8. Deletar produto
        response = self.client.delete(f'/products/{product_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar que foi deletado
        response = self.client.get(f'/products/{product_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
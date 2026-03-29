"""
Testes Automatizados para a Aplicação Shop
Arquivo: app-shop/shop/tests.py

Este arquivo contém testes para:
- Views de login e logout
- Criação de usuários
- Formulários
- Integração com API
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .forms import UserForm, ProductForm, CategoryForm, SupplierForm

# ============================================================================
# TESTES DE FORMULÁRIOS
# ============================================================================

class UserFormTest(TestCase):
    """Testes para o formulário de usuário"""

    def test_user_form_valid_data(self):
        """Testa formulário com dados válidos"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'is_staff': False
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_missing_username(self):
        """Testa formulário sem username"""
        form_data = {
            'email': 'test@example.com',
            'password': 'pass123',
            'is_staff': False
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_form_invalid_email(self):
        """Testa formulário com email inválido"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',  # Email sem @
            'password': 'pass123',
            'is_staff': False
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_form_save_method(self):
        """Testa o método save do formulário"""
        form_data = {
            'username': 'saveduser',
            'email': 'saved@example.com',
            'password': 'savedpass123',
            'is_staff': True
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.username, 'saveduser')
        self.assertEqual(user.email, 'saved@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password('savedpass123'))

class ProductFormTest(TestCase):
    """Testes para o formulário de produto"""

    def test_product_form_valid_data(self):
        """Testa formulário de produto com dados válidos"""
        form_data = {
            'name': 'Notebook',
            'description': 'Notebook para trabalho',
            'price': 3500.00,
            'stock': 10,
            'category': 1,
            'supplier': 1,
            'url_image': 'https://example.com/notebook.jpg'
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_missing_required_fields(self):
        """Testa formulário sem campos obrigatórios"""
        form_data = {
            'name': 'Produto Incompleto'
            # Faltam outros campos obrigatórios
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())

# ============================================================================
# TESTES DE VIEWS - LOGIN E LOGOUT
# ============================================================================

class LoginViewTest(TestCase):
    """Testes para a view de login"""

    def setUp(self):
        """Prepara dados para testes"""
        self.client = Client()
        self.login_url = reverse('user_login')

        # Cria usuário de teste no banco local
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_login_page_loads(self):
        """Testa se a página de login carrega corretamente"""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    @patch('shop.api_client.api_client.login_user')
    def test_login_with_valid_credentials(self, mock_login):
        """Testa login com credenciais válidas"""
        # Simula resposta bem-sucedida da API
        mock_login.return_value = {
            'success': True,
            'user': {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com',
                'is_staff': False,
                'is_active': True
            },
            'token': 'fake-jwt-token'
        }

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })

        # Deve redirecionar para a lista de produtos
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))

    @patch('shop.api_client.api_client.login_user')
    def test_login_with_invalid_credentials(self, mock_login):
        """Testa login com credenciais inválidas"""
        # Simula resposta de erro da API
        mock_login.return_value = {
            'success': False,
            'error': 'Usuário ou senha inválidos.'
        }

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        # Deve permanecer na página de login
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha inválidos.')

    def test_authenticated_user_can_access_product_list(self):
        """Testa se usuário autenticado pode acessar lista de produtos"""
        # Faz login
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    """Testes para a view de logout"""

    def setUp(self):
        """Prepara dados para testes"""
        self.client = Client()
        self.logout_url = reverse('user_logout')

        # Cria e autentica usuário
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_logout_redirects_to_product_list(self):
        """Testa se logout redireciona corretamente"""
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))

    def test_user_is_logged_out_after_logout(self):
        """Testa se o usuário está deslogado após logout"""
        self.client.get(self.logout_url)

        # Tenta acessar página protegida
        response = self.client.get(reverse('user_create'))

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)


# ============================================================================
# TESTES DE VIEWS - CRIAÇÃO DE USUÁRIO
# ============================================================================

class UserCreateViewTest(TestCase):
    """Testes para a view de criação de usuários"""

    def setUp(self):
        """Prepara dados para testes"""
        self.client = Client()
        self.create_user_url = reverse('user_create')

        # Cria usuário staff (necessário para acessar criação de usuários)
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )

    def test_non_authenticated_user_cannot_access_user_create(self):
        """Testa que usuário não autenticado não pode criar usuários"""
        response = self.client.get(self.create_user_url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_non_staff_user_cannot_access_user_create(self):
        """Testa que usuário não-staff não pode criar usuários"""
        # Cria usuário comum
        regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )
        self.client.login(username='regular', password='regular123')

        response = self.client.get(self.create_user_url)

        # Deve ser redirecionado
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_access_user_create_page(self):
        """Testa que usuário staff pode acessar página de criação"""
        self.client.login(username='staffuser', password='staffpass123')

        response = self.client.get(self.create_user_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_form.html')

    @patch('shop.api_client.api_client.create_user')
    def test_staff_user_can_create_new_user(self, mock_create_user):
        """Testa que usuário staff pode criar novo usuário"""
        self.client.login(username='staffuser', password='staffpass123')

        # Simula resposta bem-sucedida da API
        mock_create_user.return_value = {
            'id': 2,
            'username': 'newuser',
            'email': 'new@example.com',
            'is_staff': False
        }

        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'is_staff': False
        }

        response = self.client.post(self.create_user_url, form_data)

        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)

        # Verifica se a API foi chamada
        mock_create_user.assert_called_once()


# ============================================================================
# TESTES DE INTEGRAÇÃO COM API
# ============================================================================

class APIClientIntegrationTest(TestCase):
    """Testes de integração com o cliente da API"""

    @patch('shop.api_client.APIClient._get_or_refresh_token')
    @patch('requests.get')
    def test_get_products_from_api(self, mock_get, mock_token):
        """Testa obter produtos da API"""
        # Simula token
        mock_token.return_value = 'fake-token'

        # Simula resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'name': 'Produto Teste',
                'price': 100.00,
                'stock': 50
            }
        ]
        mock_get.return_value = mock_response

        from shop.api_client import api_client

        # Chama o método
        response = api_client.get_products()

        # Verifica se a requisição foi feita
        self.assertTrue(mock_get.called)


# ============================================================================
# TESTES DE PERMISSÕES
# ============================================================================

class PermissionTest(TestCase):
    """Testes para verificar permissões de acesso"""

    def setUp(self):
        """Prepara dados para testes"""
        self.client = Client()

        # Cria usuários com diferentes permissões
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123',
            is_staff=False
        )

        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )

    def test_regular_user_cannot_create_users(self):
        """Testa que usuário comum não pode criar usuários"""
        self.client.login(username='regular', password='regular123')

        response = self.client.get(reverse('user_create'))

        # Deve ser negado acesso
        self.assertNotEqual(response.status_code, 200)

    def test_staff_user_can_create_users(self):
        """Testa que usuário staff pode criar usuários"""
        self.client.login(username='staff', password='staff123')

        response = self.client.get(reverse('user_create'))

        self.assertEqual(response.status_code, 200)


# ============================================================================
# TESTES DE URLs
# ============================================================================

class URLTest(TestCase):
    """Testes para verificar se as URLs estão configuradas corretamente"""

    def test_product_list_url(self):
        """Testa URL de lista de produtos"""
        url = reverse('product_list')
        self.assertEqual(url, '/')

    def test_login_url(self):
        """Testa URL de login"""
        url = reverse('user_login')
        self.assertEqual(url, '/login/')

    def test_logout_url(self):
        """Testa URL de logout"""
        url = reverse('user_logout')
        self.assertEqual(url, '/logout/')

    def test_create_user_url(self):
        """Testa URL de criação de usuário"""
        url = reverse('user_create')
        self.assertEqual(url, '/create_user/')
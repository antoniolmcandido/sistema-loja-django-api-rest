"""
Cliente HTTP para comunicação com a API da loja.
Centraliza toda a lógica de requisições, autenticação e tratamento de erros.
"""

import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """
    Cliente para fazer requisições à API REST.

    Exemplo de uso:
        client = APIClient()
        products = client.get_products()
        new_product = client.create_product({"name": "Notebook", "price": 2000})
    """

    def __init__(self):
        """Inicializa o cliente com a URL base e token de autenticação."""
        self.base_url = settings.API_BASE_URL
        self.username = settings.API_USERNAME
        self.password = settings.API_PASSWORD
        self.token = settings.API_AUTH_TOKEN
        self.timeout = getattr(settings, 'API_REQUEST_TIMEOUT', 10)

        # Headers padrão para todas as requisições
        self.headers = {
            'username': self.username,
            'password': self.password,
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

    def _request(self, method, endpoint, data=None, params=None):
        """
        Método privado para fazer requisições HTTP.

        Args:
            method: GET, POST, PUT, PATCH, DELETE
            endpoint: caminho relativo à API (ex: 'products')
            data: payload JSON para POST/PUT/PATCH
            params: parâmetros de query string

        Returns:
            dict: resposta JSON da API

        Raises:
            requests.RequestException: em caso de erro na requisição
        """
        url = f"{self.base_url}/{endpoint}/"

        try:
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )

            elif method.upper() == 'POST':
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )

            elif method.upper() == 'PUT':
                response = requests.put(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )

            elif method.upper() == 'PATCH':
                response = requests.patch(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )

            elif method.upper() == 'DELETE':
                response = requests.delete(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )

            else:
                raise ValueError(f"Método HTTP inválido: {method}")

            # Verificar se a requisição foi bem-sucedida
            response.raise_for_status()

            # Retornar dados JSON (alguns endpoints DELETE retornam vazio)
            if response.status_code == 204:
                return None

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout na requisição para {url}")
            raise

        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão com a API: {url}")
            raise

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {response.status_code}: {response.text}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise

    def _request_with_id(self, method, endpoint, pk, data=None):
        """
        Método para requisições que precisam de um ID específico.

        Args:
            method: GET, POST, PUT, PATCH, DELETE
            endpoint: caminho relativo (ex: 'products')
            pk: ID do recurso
            data: payload JSON

        Returns:
            dict: resposta JSON da API
        """
        url = f"{self.base_url}/{endpoint}/{pk}/"

        try:
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )

            elif method.upper() == 'PUT':
                response = requests.put(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )

            elif method.upper() == 'PATCH':
                response = requests.patch(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )

            elif method.upper() == 'DELETE':
                response = requests.delete(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )

            else:
                raise ValueError(f"Método HTTP inválido: {method}")

            response.raise_for_status()

            if response.status_code == 204:
                return None

            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {response.status_code}: {response.text}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            raise

    # ===== MÉTODOS PARA CATEGORIAS =====

    def get_categories(self, page=1):
        """
        Obter lista de todas as categorias.

        Returns:
            dict: contendo 'results' (lista de categorias) e paginação
        """
        return self._request('GET', 'categories', params={'page': page})

    def get_category(self, pk):
        """Obter uma categoria específica pelo ID."""
        return self._request_with_id('GET', 'categories', pk)

    def create_category(self, data):
        """
        Criar uma nova categoria.

        Args:
            data: dict com {'name': str, 'description': str}

        Returns:
            dict: dados da categoria criada
        """
        return self._request('POST', 'categories', data=data)

    def update_category(self, pk, data):
        """Atualizar uma categoria."""
        return self._request_with_id('PUT', 'categories', pk, data=data)

    def partial_update_category(self, pk, data):
        """Atualizar parcialmente uma categoria."""
        return self._request_with_id('PATCH', 'categories', pk, data=data)

    def delete_category(self, pk):
        """Deletar uma categoria."""
        return self._request_with_id('DELETE', 'categories', pk)

    # ===== MÉTODOS PARA FORNECEDORES =====

    def get_suppliers(self, page=1):
        """Obter lista de todos os fornecedores."""
        return self._request('GET', 'suppliers', params={'page': page})

    def get_supplier(self, pk):
        """Obter um fornecedor específico pelo ID."""
        return self._request_with_id('GET', 'suppliers', pk)

    def create_supplier(self, data):
        """
        Criar um novo fornecedor.

        Args:
            data: dict com {'name': str, 'contact_email': str, 'phone': str, 'address': str}

        Returns:
            dict: dados do fornecedor criado
        """
        return self._request('POST', 'suppliers', data=data)

    def update_supplier(self, pk, data):
        """Atualizar um fornecedor."""
        return self._request_with_id('PUT', 'suppliers', pk, data=data)

    def partial_update_supplier(self, pk, data):
        """Atualizar parcialmente um fornecedor."""
        return self._request_with_id('PATCH', 'suppliers', pk, data=data)

    def delete_supplier(self, pk):
        """Deletar um fornecedor."""
        return self._request_with_id('DELETE', 'suppliers', pk)

    # ===== MÉTODOS PARA PRODUTOS =====

    def get_products(self, page=1, category_id=None, supplier_id=None, search=None):
        """
        Obter lista de produtos com filtros opcionais.

        Args:
            page: número da página
            category_id: filtrar por categoria (opcional)
            supplier_id: filtrar por fornecedor (opcional)
            search: termo de busca (opcional)

        Returns:
            dict: contendo 'results' (lista de produtos) e paginação
        """
        params = {'page': page}

        if category_id:
            params['category'] = category_id

        if supplier_id:
            params['supplier'] = supplier_id

        if search:
            params['search'] = search

        return self._request('GET', 'products', params=params)

    def get_product(self, pk):
        """Obter um produto específico pelo ID."""
        return self._request_with_id('GET', 'products', pk)

    def create_product(self, data):
        """
        Criar um novo produto.

        Args:
            data: dict com {
                'name': str,
                'description': str,
                'price': float,
                'stock': int,
                'category': int (ID),
                'supplier': int (ID),
                'url_image': str (opcional)
            }

        Returns:
            dict: dados do produto criado
        """
        return self._request('POST', 'products', data=data)

    def update_product(self, pk, data):
        """Atualizar um produto (todos os campos)."""
        return self._request_with_id('PUT', 'products', pk, data=data)

    def partial_update_product(self, pk, data):
        """Atualizar parcialmente um produto (apenas campos fornecidos)."""
        return self._request_with_id('PATCH', 'products', pk, data=data)

    def delete_product(self, pk):
        """Deletar um produto."""
        return self._request_with_id('DELETE', 'products', pk)


# Criar uma instância global do cliente para usar em toda a aplicação
api_client = APIClient()
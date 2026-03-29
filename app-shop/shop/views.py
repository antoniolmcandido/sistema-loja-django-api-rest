from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .api_client import api_client
from .forms import ProductForm, CategoryForm, SupplierForm, UserForm
import logging
from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)

def is_staff_user(user):
    return user.is_staff

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        api_response = api_client.login_user(username, password)

        if api_response['success']:
            # Login local para manter sessão Django
            user = authenticate(request, username=username, password=password)
            
            # Se usuário não existe localmente, criar
            if user is None:
                user_data = api_response['user']
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': user_data.get('email', ''),
                        'is_staff': user_data.get('is_staff', False),
                        'is_active': user_data.get('is_active', True)
                    }
                )
                # Definir senha apenas se criou novo
                if created:
                    user.set_password(password)
                    user.save()
                
                # Autenticar novamente
                user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect("product_list")
        
        return render(request, "login.html", {
            "error": api_response.get('error', 'Usuário ou senha inválidos.')
        })
    
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    cache.delete('api_jwt_token')
    return redirect("product_list")

@login_required(login_url='user_login')
@user_passes_test(is_staff_user)
def user_create(request):
    """
    Usuários são criados via API.
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                user_data = {
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'password': form.cleaned_data['password'],
                    'is_staff': form.cleaned_data['is_staff'],
                }
                
                # Criar via API
                api_client.create_user(user_data)
                messages.success(request, "Usuário criado com sucesso!")
                return redirect("product_list")
                
            except Exception as e:
                logger.error(f"Erro ao criar usuário via API: {str(e)}")
                messages.error(request, f"Erro ao criar usuário: {str(e)}")
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form})

# ===== PRODUTOS =====

def product_list(request):
    """
    Listar produtos usando a API.
    """
    try:
        # Buscar produtos da API
        response = api_client.get_products(page=1)

        # Extrair resultados
        produtos = response.get('results', [])

        # Informações de paginação
        total_count = response.get('count', 0)

        # Criar um objeto paginator simples
        paginator = Paginator(produtos, 3)
        page_number = request.GET.get('page', 1)
        produtos = paginator.get_page(page_number)

        return render(request, 'product_list.html', {
            'produtos': produtos,
            'total_count': total_count
        })

    except Exception as e:
        logger.error(f"Erro ao buscar produtos da API: {str(e)}")
        messages.error(
            request,
            "Erro ao conectar com a API. Tente novamente mais tarde."
        )
        return render(request, 'product_list.html', {
            'produtos': [],
            'error': str(e)
        })

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_create(request):
    """
    Criar produto usando a API.
    """
    # Buscar categorias e fornecedores da API
    try:
        categories_response = api_client.get_categories()
        suppliers_response = api_client.get_suppliers()

        categories = categories_response.get('results', [])
        # ordenar categorias por nome
        categories.sort(key=lambda x: x['name'])

        suppliers = suppliers_response.get('results', [])
        # ordenar fornecedores por nome
        suppliers.sort(key=lambda x: x['name'])

    except Exception as e:
        logger.error(f"Erro ao buscar categorias/fornecedores: {str(e)}")
        categories = []
        suppliers = []
        messages.error(request, "Erro ao carregar categorias/fornecedores.")

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # Preparar dados para enviar à API
                product_data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'price': str(form.cleaned_data['price']),  # Converter para string
                    'stock': form.cleaned_data['stock'],
                    'category': form.cleaned_data['category'],
                    'supplier': form.cleaned_data['supplier'],
                }

                # Adicionar URL da imagem se fornecida
                if form.cleaned_data.get('url_image'):
                    product_data['url_image'] = form.cleaned_data['url_image']

                # Enviar à API
                api_client.create_product(product_data)
                messages.success(request, "Produto criado com sucesso!")
                return redirect('product_list')

            except Exception as e:
                logger.error(f"Erro ao criar produto via API: {str(e)}")
                messages.error(request, f"Erro ao criar produto: {str(e)}")

    else:
        form = ProductForm()

    # Modificar o formulário para usar dados da API
    # Isto será tratado na Parte 2.5
    return render(request, 'product_form.html', {
        'form': form,
        'categories': categories,
        'suppliers': suppliers
    })

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_update(request, pk=1):
    """
    Atualizar produto usando a API.
    """
    try:
        # Buscar produto por ID
        product = api_client.get_product(pk)

        # Buscar categorias e fornecedores
        categories_response = api_client.get_categories()
        suppliers_response = api_client.get_suppliers()

        categories = categories_response.get('results', [])
        suppliers = suppliers_response.get('results', [])

    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        messages.error(request, "Erro ao carregar produto.")
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # Preparar dados para atualizar
                product_data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                    'price': str(form.cleaned_data['price']),
                    'stock': form.cleaned_data['stock'],
                    'category': form.cleaned_data['category'],
                    'supplier': form.cleaned_data['supplier'],
                }

                if form.cleaned_data.get('url_image'):
                    product_data['url_image'] = form.cleaned_data['url_image']

                # Enviar à API
                api_client.update_product(pk, product_data)
                messages.success(request, "Produto atualizado com sucesso!")
                return redirect('product_list')

            except Exception as e:
                logger.error(f"Erro ao atualizar produto via API: {str(e)}")
                messages.error(request, f"Erro ao atualizar produto: {str(e)}")

    else:
        form = ProductForm(initial=product)
        initial_data = {
            'name': product.get('name'),
            'description': product.get('description'),
            'price': product.get('price'),
            'stock': product.get('stock'),
            'url_image': product.get('url_image'),
            # Extrair apenas o ID se for dict, ou usar o valor direto se já for int
            'category': product.get('category') if isinstance(product.get('category'), int) else product.get('category', {}).get('id'),
            'supplier': product.get('supplier') if isinstance(product.get('supplier'), int) else product.get('supplier', {}).get('id'),
        }
        form = ProductForm(initial=initial_data)

    return render(request, 'product_form.html', {
        'form': form,
        'categories': categories,
        'suppliers': suppliers
    })

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_delete(request, pk):
    """
    Deletar produto usando a API.
    """
    try:
        product = api_client.get_product(pk)

    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        messages.error(request, "Erro ao carregar produto.")
        return redirect('product_list')

    if request.method == 'POST':
        try:
            api_client.delete_product(pk)
            messages.success(request, "Produto deletado com sucesso!")
            return redirect('product_list')

        except Exception as e:
            logger.error(f"Erro ao deletar produto: {str(e)}")
            messages.error(request, f"Erro ao deletar produto: {str(e)}")
            return redirect('product_list')

    return render(request, 'product_confirm_delete.html', {'product': product})

# ===== CATEGORIAS =====

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def category_create(request):
    """
    Criar categoria usando a API.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category_data = {
                    'name': form.cleaned_data['name'],
                    'description': form.cleaned_data['description'],
                }

                api_client.create_category(category_data)
                messages.success(request, "Categoria criada com sucesso!")
                return redirect('product_create')

            except Exception as e:
                logger.error(f"Erro ao criar categoria via API: {str(e)}")
                messages.error(request, f"Erro ao criar categoria: {str(e)}")

    else:
        form = CategoryForm()

    return render(request, 'category_form.html', {'form': form})

# ===== FORNECEDORES =====

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def supplier_create(request):
    """
    Criar fornecedor usando a API.
    """
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            try:
                supplier_data = {
                    'name': form.cleaned_data['name'],
                    'contact_email': form.cleaned_data['contact_email'],
                    'phone': form.cleaned_data['phone'],
                    'address': form.cleaned_data['address'],
                }

                api_client.create_supplier(supplier_data)
                messages.success(request, "Fornecedor criado com sucesso!")
                return redirect('product_create')

            except Exception as e:
                logger.error(f"Erro ao criar fornecedor via API: {str(e)}")
                messages.error(request, f"Erro ao criar fornecedor: {str(e)}")

    else:
        form = SupplierForm()

    return render(request, 'supplier_form.html', {'form': form})

def custom_page_not_found_view(request):
    return render(request, "404.html", status=404)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .api_client import api_client
from .forms import ProductForm, CategoryForm, SupplierForm, UserForm
import logging

logger = logging.getLogger(__name__)

def is_staff_user(user):
    return user.is_staff

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("product_list")
        else:
            return render(request, "login.html", {"error_message": "Usuário ou senha inválidos."})
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("product_list")

@login_required(login_url='user_login')
@user_passes_test(is_staff_user)
def user_create(request):
    """
    NOTA: Criação de usuários ainda acessa o banco direto.
    Usuários são criados apenas via Django Admin por segurança.
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("product_list")
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
                    'category': form.cleaned_data['category'].id,
                    'supplier': form.cleaned_data['supplier'].id,
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
                    'category': form.cleaned_data['category'].id,
                    'supplier': form.cleaned_data['supplier'].id,
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
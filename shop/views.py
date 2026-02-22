from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category, Supplier
from .forms import ProductForm, CategoryForm, SupplierForm, UserForm

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
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Não salva ainda no banco
            user.set_password(form.cleaned_data["password"])  # Faz o hash da senha
            user.save()  # Agora salva com a senha hashada
            return redirect("product_list")
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form})

# Create your views here.
def product_list(request):
    produtos = Product.objects.all() # ORM
    paginator = Paginator(produtos, 3)

    page_number = request.GET.get('page')
    produtos = paginator.get_page(page_number)

    return render(request, 'product_list.html', {'produtos': produtos})

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_create(request):
    if request.method == 'POST':
        # Se o método for POST, o formulário foi enviado
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()  # Salva o novo produto no banco de dados
            return redirect('product_list')  # Redireciona para a lista de produtos
    else:
        # Se o método for GET, exibe um formulário em branco
        form = ProductForm()

    # Renderiza o template do formulário, passando o form como contexto
    return render(request, 'product_form.html', {'form': form})

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'product_form.html', {'form': form})

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    
    return render(request, 'product_confirm_delete.html', {'product': product})

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_create')
    else:
        form = CategoryForm()

    return render(request, 'category_form.html', {'form': form})

@login_required(login_url="user_login")
@user_passes_test(is_staff_user)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_create')
    else:
        form = SupplierForm()

    return render(request, 'supplier_form.html', {'form': form})

def custom_page_not_found_view(request):
    # You can add custom logic here
    return render(request, "404.html", status=404)
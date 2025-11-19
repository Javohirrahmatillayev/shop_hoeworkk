from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Category, Product, Order, ProductComment
from .forms import CustomUserCreationForm, ProductForm, CategoryForm, ProductCommentForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required   
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q



def index(request,category_id = None):
    
    categories = Category.objects.all()
    
    if category_id:
        products = Product.objects.filter(category = category_id)
    else:
        products = Product.objects.all()

    context = {
        'categories':categories,
        'products':products
    }
    return render(request,'app/home.html',context)


def home(request):
    filter_type = request.GET.get('filter')  

    products = Product.objects.all()

    if filter_type == 'cheap':
        products = products.order_by('price')  
    elif filter_type == 'expensive':
        products = products.order_by('-price')  

    context = {
        'products': products,
        'filter_type': filter_type,
    }
    return render(request, 'app/home.html', context)



def view_product(request, pk):
    product = get_object_or_404(Product, pk = pk)
    return render(request, 'app/detail.html', {'product' : product})

from .forms import CustomUserCreationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('app:index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can login now.")
            return redirect('app:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('app:index')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:index')
            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Please correct the errors below")
    return render(request, 'app/login.html', {'form': form})    

def logout_view(request):
    logout(request)
    return redirect('app:index')

@login_required
def add_category(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to add categories.")

    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Product added successfully!")
        return redirect('app:index')  

    return render(request, 'app/add_category.html', {'form': form})

@login_required
def add_product_view(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed to add products.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('app:index')
    else:
        form = ProductForm()
    
    return render(request, 'app/add_product.html', {'form': form})

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.user.role != 'admin':
        messages.error(request, "You are not allowed to edit this product.")
        return redirect('app:product_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('app:product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'app/update_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.user.role != 'admin':
        messages.error(request, "You are not allowed to delete this product.")
        return redirect('app:product_detail', pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('app:index')
    
    return render(request, 'app/delete_product.html', {'product': product})


@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        quantity = int(request.POST.get("quantity"))
        price = request.POST.get("price")

        if quantity > product.stock:
            return HttpResponse("Yetarli stock yo'q!")

        product.stock -= quantity
        product.save()

        Order.objects.create(
            user=request.user,
            phone=phone,
            quantity=quantity,
            product=product,
            price = price 
        )

        return redirect("app:index") 
    return render(request, "app/detail.html", {"product": product})



def orders_list(request):
    orders = Order.objects.all()  
    context = {
        'orders': orders
    }
    return render(request, 'app/orders_list.html', context)

@login_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if not Order.objects.filter(user=request.user, product=product).exists():
        return HttpResponse('You must order this product before commenting.')
    
    if ProductComment.objects.filter(user=request.user, product=product).exists():
        return HttpResponse('You have already commented on this product.')
    
    if request.method == 'POST':
        form = ProductCommentForm(request.POST)
        if form.is_valid():
            ProductComment.objects.create(
                product=product,
                user=request.user,
                comment=form.cleaned_data['comment']
            )
            return redirect('app:product_detail', product_id=product.id)
    else:
        form = ProductCommentForm()

    return render(request, 'detail.html', {'form': form, 'product': product })

    
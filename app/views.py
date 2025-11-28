from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Category, Product, Order, ProductComment
from .forms import CustomUserCreationForm, ProductForm, CategoryForm, ProductCommentForm, EmailForm, PhoneLoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required   
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Avg
from django.core.mail import send_mail
from django.db.models import Q
from app.utils import filter_by_price



def index(request,category_id = None):
    search_query = request.GET.get('q','')
    filter_type = request.GET.get('filter_type','')
    
    categories = Category.objects.all()
    
    if category_id:
        products = Product.objects.filter(category = category_id)
    else:
        products = Product.objects.all()
        
    if search_query:
        products = products.filter(Q(name__icontains = search_query) | Q(description__icontains=search_query))

    products = filter_by_price(filter_type,products)

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
    related_products = Product.objects.filter(category = product.category).exclude(id = product.pk)
    comments = ProductComment.objects.filter(product=product)
    avg_rating = comments.aggregate(avg=Avg('rating'))['avg']
    if avg_rating is None:
        avg_rating = 0
    
    can_comment = False
    if request.user.is_authenticated:
        can_comment = Order.objects.filter(user=request.user, product=product).exists()
    
    form = ProductCommentForm()
        
    if request.method == 'POST' and can_comment:
        form = ProductCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('app:product_detail', pk = pk )
    
    
    context = {
        'product' : product,
        'related_products' : related_products,
        'comments' : comments,
        'can_comment' : can_comment, 
        'form':form,
        'avg_rating':avg_rating,
    }
    
    return render(request, 'app/detail.html', context)


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

    form = PhoneLoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            user = authenticate(request, phone_number=phone, password=password)

            if user is not None:
                login(request, user)
                return redirect('app:index')
            else:
                messages.error(request, "Telefon raqam yoki parol noto'g'ri")
        else:
            messages.error(request, "Formada xatolik bor")

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

def contact_us(request):
    return render(request, 'app/contact_us.html')

def sending_message_to_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender_email = form.cleaned_data['sender_email']
            
            full_message = f"From: {sender_email}\n\n{message}"
            
            send_mail(subject, 
                      full_message, 
                      'deozey7@gmail.com',
                      ['deozey7@gmail.com'],
                      )
            return render(request, 'app/success.html')
    else:
        form = EmailForm()
    return render(request, 'app/send_mail.html', {'form' : form})   
    
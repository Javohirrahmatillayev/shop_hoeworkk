from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def index(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {
        'categories' : categories,
        'products' : products
    }
    return render(request, 'app/home.html', context)

def view_product(request, pk):
    product = get_object_or_404(Product, pk = pk)
    return render(request, 'app/detail.html', {'product' : product})



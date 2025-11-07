from django.urls import path, include
from .views import index, view_product

app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:pk>/', view_product, name='product_detail')
]
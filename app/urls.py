from django.urls import path, include
from .views import index, view_product, login_view, register_view, logout_view, add_product_view, delete_product, update_product

app_name = 'app'

urlpatterns = [
    path('', index, name='index'),
    path('category/<int:category_id>',index,name='products_of_category'),
    path('product/<int:pk>/', view_product, name='product_detail'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('product/add/', add_product_view, name='add_product'),
    path('product/<int:pk>/edit/', update_product, name='update_product'),        
    path('product/<int:pk>/delete/', delete_product, name='delete_product'),
]
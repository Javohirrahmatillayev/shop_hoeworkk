from django.urls import path, include
from .views import (HomeView, 
                    ProductDetailView,
                    LoginView,
                    RegisterView, 
                    LogoutView, 
                    AddProductView,
                    DeleteProductView, 
                    UpdateProductView, 
                    AddCategoryView, 
                    PlaceOrderView, 
                    OrdersListView,
                    ContactUsView,
                    SendEmailView)

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<int:category_id>',HomeView.as_view(),name='category_products'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('product/add/', AddProductView.as_view(), name='add_product'),
    path('product/<int:pk>/edit/', UpdateProductView.as_view(), name='update_product'),        
    path('product/<int:pk>/delete/', DeleteProductView.as_view(), name='delete_product'),
    path('add-category/', AddCategoryView.as_view(), name='add_category'),
    path('order/<int:product_id>/', PlaceOrderView.as_view(), name='place_order'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('send-email/', SendEmailView.as_view(), name='send_email'),
    path('contact_us/', ContactUsView.as_view(), name='contact_us')
]
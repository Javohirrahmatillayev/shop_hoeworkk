from django.contrib import admin
from .models import Category, Product, CustomUser, ProductComment, Order
from django.urls import reverse 
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from import_export import resources
from import_export.admin import ImportExportModelAdmin  

User = get_user_model()

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock', 'created_at')
        
class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            "id",
            "user__username",
            "product__name",
            "phone",
            "quantity",
            "price",
            "created_at",
        )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = ("id", "username", "email")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product_count')
    search_fields = ('title',)
    ordering = ('id',)
    
    def product_count(self, obj):
        count = obj.products.count()
        
        app_label = obj._meta.app_label
        model_name = obj.products.model._meta.model_name
    
        url = (
            reverse(f'admin:{app_label}_{model_name}_changelist')
            + f'?category__id__exact={obj.id}'
        )
        
        return format_html('<a href="{}">{}</a>', url, count)
            
    product_count.short_description = 'Products'
    
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

    list_display = ("id", "name", "price", "stock", "product_image")
    search_fields = ("name",)
    list_filter = ("price",)
    ordering = ("id",)

    def product_image(self, obj):
        return format_html('<img src="{}" width="60" style="border-radius:5px;" />', obj.image_url)
    product_image.short_description = "Image"





@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource

    list_display = (
        "id",
        "user",
        "product",
        "phone",
        "quantity",
        "price",
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
        "phone",
    )

    list_filter = (
        "created_at",
        "product",
        "user",
    )

    ordering = ("-created_at",)


    
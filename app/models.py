from django.db import models
from decimal import Decimal
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings




class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    


class Category(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Categories'



class Product(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.PositiveSmallIntegerField(default=1)
    discount = models.PositiveSmallIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                 related_name='products',
                                 null=True, blank=True)
    
    @property
    def discounted_price(self):
        if self.discount:
            return self.price * Decimal(f'{(1 - self.discount / 100)}') 
        
        return self.price
    
    @property
    def image_url(self):
        if not self.image:
            return static('app/image/not_found_image.jpg')
        return self.image.url
    
    
    def __str__(self):
        return self.name 
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'), 
    )       
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user."
    )
    

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE )
    phone = models.CharField(max_length=20)
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ProductComment(BaseModel):
    class RatingChoices(models.IntegerChoices):
        ONE = 1, '★☆☆☆☆'
        TWO = 2, '★★☆☆☆'
        THREE = 3, '★★★☆☆'
        FOUR = 4, '★★★★☆'
        FIVE = 5, '★★★★★'

        
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RatingChoices.choices, default = RatingChoices.FIVE)
    file = models.ImageField(upload_to='products/', null=True, blank=True)
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
        



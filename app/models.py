from django.db import models
from decimal import Decimal


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
    
    
    def __str__(self):
        return self.name

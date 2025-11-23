from .models import Product, Category
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Product modeli uchun
@receiver(post_save, sender= Product)
def post_save_product(sender, instance, created, *args, **kwargs):
    if created:
        print("Product created!, Product id: ", instance.id)
    else:
        print("Product updated!, Product id: ", instance.id)

@receiver(pre_save, sender= Product)        
def pre_save_product(sender, instance, *args, **kwargs):
    print("Product is creating!, Product id: ", instance.id)
    


# Category modeli uchun
@receiver(post_save, sender= Category)
def post_save_category(sender, instance, created, *args, **kwargs):
    if created:
        print("Category created!, Category id: ", instance.id)
    else:
        print("Category updated!, Category id: ", instance.id)

@receiver(pre_save, sender= Category)        
def pre_save_category(sender, instance, *args, **kwargs):
    print("Category is creating!, Category id: ", instance.id)
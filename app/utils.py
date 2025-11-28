from django.db.models import Avg
from django.db.models.functions import Round


def filter_by_price(filter_type : str,products = None):
    if filter_type == 'expensive':
        products = products.order_by('-price')
        
    elif filter_type == 'cheap':
        products = products.order_by('price')
        
    elif filter_type == 'rating':
        products = products.annotate(avg_rating = Round(Avg('comments__rating'))).order_by('-avg_rating')
    else:
        products = products.all()

    return products
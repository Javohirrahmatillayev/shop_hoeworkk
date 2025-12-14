from django.views import View
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
from django.views.generic import DetailView, ListView, FormView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy




class HomeView(ListView):
    model = Product
    template_name = 'app/home.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = Product.objects.all()
        
        category_id = self.kwargs.get('category_id')
        search_query = self.request.GET.get('q', '')
        filter_type = self.request.GET.get('filter') or self.request.GET.get('filter_type', '')
        
        if category_id:
            queryset = queryset.filter(category = category_id)
            
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if filter_type == 'cheap':
            queryset = queryset.order_by('price')
        elif filter_type == 'expensive':
            queryset = queryset.order_by('-price')
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'app/detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object 
        
        comments = ProductComment.objects.filter(product=product)
        avg_rating = comments.aggregate(avg=Avg('rating'))['avg'] or 0
        
        can_comment = False
        if self.request.user.is_authenticated:
            can_comment = Order.objects.filter(
                user = self.request.user,
                product = product
            ).exists()
            
        context.update({
            'related_products': Product.objects.filter(
                category = product.category
            ).exclude(pk=product.pk),
            'comments':comments,
            'avg_rating':avg_rating,
            'can_comment':can_comment,
            'form':ProductCommentForm(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        can_comment = request.user.is_authenticated and Order.objects.filter(
            user = request.user,
            product = self.object
        ).exists()
        
        if not can_comment:
            return redirect('app:product_detail', pk=self.object.pk)
        
        form = ProductCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = self.object
            comment.save()
            messages.success(request, "Comment added succesfully!")
            
        return redirect('app:product_detail', pk= self.object.pk)


class RegisterView(FormView):
    template_name = 'app/register.html'
    form_class = CustomUserCreationForm
    success_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Account created succesfully! You can login now."
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below."
        )
        return super().form_invalid(form)



class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = PhoneLoginForm()
        return render(request, 'app/login.html', {'form':form})
    
    def post(self, request, *args, **kwargs):
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            user = authenticate(request, phone_number = phone, password=password)
            if user is not None:
                login(request, user)
                return redirect('app:home')
            else:
                messages.error(request, "Phone number or password is wrong!")
        else:
            messages.error(request, "There is an error in the form.")
        return render(request, 'app/login.html', {'form':form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('app:home')


class AddCategoryView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app/add_category.html'
    success_url = reverse_lazy('app:home')
    login_url = 'app:login'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden('You are not allowed to add categories.')
        return super().handle_no_permissions()
    
    def form_valid(self, form):
        messages.success(self.request, "Category added succesfully!")
        return super().form_valid(form)


class AddProductView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/add_product.html'
    success_url = reverse_lazy('app:home')
    login_url = 'app:login'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("You are not allowed to add products.")
        return super().handle_no_permission()
    
    def form_valid(self, form):
        messages.success(self.request, "Product added succesfully!")
        return super().form_valid(form)


class UpdateProductView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/update_product.html'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You are not allowed to edit this product.")
            return redirect('app:product_detail', pk=self.kwargs.get('pk'))
        return super().handle_no_permission()
    
    def form_valid(self, form):
        messages.success(self.request, "Product updated succesfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('app:product_detail', kwargs={'pk':self.object.pk})


class DeleteProductView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'app/delete_product.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('app:home')
    login_url = 'app:login'
    
    def test_func(self):
        return self.request.user.role == 'admin'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You are not allowed to delete this product.")
            return redirect('app:product_detail', pk=self.kwargs.get('pk'))
        return super().handle_no_permission()
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Product deleted succesfully!")
        return super().delete(request, *args, **kwargs)


class PlaceOrderView(LoginRequiredMixin, View):
    login_url = 'app:login'
    
    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'app/detail.html', {'product':product})
    
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id = product_id)
        
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        quantity = int(request.POST.get("quantity", 0))
        price = request.POST.get("price")
        
        if quantity > product.stock:
            return HttpResponse("Not enough stock!")
        
        product.stock -= quantity
        product.save()
        
        Order.objects.create(
            user = request.user, 
            phone = phone, 
            quantity = quantity, 
            product = product,
            price = price
        )
        
        return redirect("app:home")



class OrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'app/orders_list.html'
    context_object_name = 'orders'
    login_url = 'app:login'
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class ContactUsView(TemplateView):
    template_name = 'app/contact_us.html'
 

class SendEmailView(FormView):
    template_name = 'app/send_mail.html'
    form_class = EmailForm
    success_url = reverse_lazy('app:success')
    
    def form_valid(self, form):
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender_email = form.cleaned_data['sender_email']
        
        full_message = f"From: {sender_email}\n\n{message}"
        
        send_mail(
            subject, 
            full_message,
            'deozey7@gmail.com',
            ['deozey7@gmail.com'],
        )
        return super().form_valid(form)
    
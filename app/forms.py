from .models import CustomUser, Product, Category, ProductComment
from django import forms
from django.core.validators import RegexValidator

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    phone_regex = RegexValidator(
        regex=r'^\+9989\d{8}$',
        message="Phone number must be entered in the format: '+9989XXXXXXXX'."   # nomerni shu formatda kiritilgan yoki kiritilmaganligini tekshirish uchun 
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        required=True,
        label="Phone Number"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'role']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return p2
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price','description', 'stock', 'discount', 'image', 'category']
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input-box',
                'placeholder': 'Kategoriya nomi'
            })
        }

class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['comment', 'rating', 'file']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            }),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),      
        },
        labels = {
            'comment': '',
            'rating': 'Rating',
            'file': 'Upload Image (optional)'
        }
        
class EmailForm(forms.Form):
    subject = forms.CharField(max_length=60)
    message = forms.CharField(widget=forms.Textarea)
    sender_email = forms.EmailField(label="Your Email")
    
class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(label="Phone Number")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


        
        

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto, Categoria


# ==================================================
# FORMULARIO DE REGISTRO DE USUARIO
# ==================================================
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(max_length=50, required=True, label="Nombre")
    last_name = forms.CharField(max_length=50, required=True, label="Apellido")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este usuario ya existe.")
        return username


# ==================================================
# FORMULARIO DE PRODUCTO
# ==================================================
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Camisa de lino premium',
                'class': 'form-input'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Describe el producto: material, talla, color...',
                'rows': 4,
                'class': 'form-input'
            }),
            'precio': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'class': 'form-input'
            }),
            'stock': forms.NumberInput(attrs={
                'placeholder': '0',
                'min': '0',
                'class': 'form-input'
            }),
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'imagen': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-file',
                'id': 'id_imagen'
            }),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock

    def clean_imagen(self):
        """Valida que la imagen no pese demasiado ni tenga formato raro."""
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError("La imagen no puede pesar más de 5 MB.")
            nombre = imagen.name.lower()
            if not nombre.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                raise forms.ValidationError("Solo se permiten imágenes JPG, PNG, WEBP o GIF.")
        return imagen


# ==================================================
# FORMULARIO DE CATEGORÍA
# ==================================================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Camisas, Pantalones, Vestidos...',
                'class': 'form-input'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Describe brevemente esta categoría (opcional)',
                'rows': 3,
                'class': 'form-input'
            }),
        }

    def clean_nombre(self):
        """Evita duplicados (ignorando mayúsculas) excepto al editar la misma."""
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre no puede estar vacío.")

        qs = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe una categoría con este nombre.")
        return nombre
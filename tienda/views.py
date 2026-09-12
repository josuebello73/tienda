from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Pedido, Producto, Categoria 
from .cart import Carrito

#registro de usuario
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_productos')
    else:
        form = UserCreationForm()
    return render(request, 'tienda/registro.html', {'form': form})
# READ - Listar
def lista_productos(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'tienda/lista.html', {'productos': productos})

# READ - Detalle
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'tienda/detalle.html', {'producto': producto})

# CREATE
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        categoria_id = request.POST['categoria']
        Producto.objects.create(
            nombre=nombre, descripcion=descripcion, precio=precio,
            stock=stock, categoria_id=categoria_id
        )
        return redirect('lista_productos')
    categorias = Categoria.objects.all()
    return render(request, 'tienda/crear.html', {'categorias': categorias})

# UPDATE
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.stock = request.POST['stock']
        producto.save()
        return redirect('lista_productos')
    categorias = Categoria.objects.all()
    return render(request, 'tienda/editar.html', {'producto': producto, 'categorias': categorias})

# DELETE
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'tienda/eliminar.html', {'producto': producto})

# Create your views here.

# carrito
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.agregar(producto)
    return redirect('ver_carrito')

def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'tienda/carrito.html', {'carrito': carrito})

def eliminar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.eliminar(producto)
    return redirect('ver_carrito')

@login_required
def pago_transferencia(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == 'POST':
        pedido.referencia_transferencia = request.POST.get('referencia', '')
        if 'comprobante' in request.FILES:
            pedido.comprobante = request.FILES['comprobante']
        pedido.estado = 'pagado'
        pedido.save()
        return redirect('confirmacion_pedido', pedido_id=pedido.id)
    return render(request, 'tienda/pago_transferencia.html', {'pedido': pedido})
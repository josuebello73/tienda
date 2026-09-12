from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria

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

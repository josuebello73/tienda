# ==================================================
# IMPORTS
# ==================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, F, Count, Q

from .models import Producto, Categoria, Pedido, PedidoItem
from .cart import Carrito
from .forms import RegistroForm, ProductoForm, CategoriaForm
import uuid
from django.utils import timezone


# ==================================================
# AUTENTICACIÓN
# ==================================================
def inicio(request):
    """Página de inicio principal de la tienda (Landig page)."""
    return render(request, 'tienda/inicio.html')

def registro(request):
    """Registro de usuario con formulario extendido."""
    if request.user.is_authenticated:
        return redirect('lista_productos')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada.")
            return redirect('lista_productos')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = RegistroForm()

    return render(request, 'tienda/registro.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('lista_productos')


# ==================================================
# CATÁLOGO PÚBLICO
# ==================================================
def lista_productos(request):
    """Catálogo público con filtros, búsqueda y ordenamiento."""
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Búsqueda por nombre
    q = request.GET.get('q')
    if q:
        productos = productos.filter(nombre__icontains=q)

    # Filtros de precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Ordenamiento
    orden = request.GET.get('orden')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nuevo':
        productos = productos.order_by('-creado')
    else:
        productos = productos.order_by('-creado')

    return render(request, 'tienda/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
    })


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'tienda/detalle.html', {'producto': producto})


# ==================================================
# CARRITO
# ==================================================
@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if producto.stock <= 0:
        messages.error(request, "Producto agotado.")
        return redirect('lista_productos')

    carrito = Carrito(request)
    carrito.agregar(producto)
    messages.success(request, f"'{producto.nombre}' agregado al carrito.")
    return redirect('ver_carrito')


@login_required
def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'tienda/carrito.html', {'carrito': carrito})


@login_required
def eliminar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = Carrito(request)
    carrito.eliminar(producto)
    messages.success(request, f"'{producto.nombre}' eliminado del carrito.")
    return redirect('ver_carrito')


@login_required
def actualizar_cantidad(request, producto_id):
    """Actualiza la cantidad de un producto en el carrito."""
    if request.method != 'POST':
        return redirect('ver_carrito')

    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        messages.error(request, "Cantidad inválida.")
        return redirect('ver_carrito')

    producto = get_object_or_404(Producto, id=producto_id)

    if cantidad < 1:
        messages.warning(request, "La cantidad mínima es 1.")
        return redirect('ver_carrito')

    if cantidad > producto.stock:
        messages.error(
            request,
            f"Solo hay {producto.stock} unidades de '{producto.nombre}' disponibles."
        )
        return redirect('ver_carrito')

    carrito = Carrito(request)
    carrito.carrito[str(producto_id)]['cantidad'] = cantidad
    carrito.guardar()

    messages.success(request, f"Cantidad de '{producto.nombre}' actualizada.")
    return redirect('ver_carrito')
# ==================================================
# CHECKOUT Y PEDIDOS
# ==================================================
@login_required
def checkout(request):
    carrito = Carrito(request)

    if len(carrito) == 0:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('lista_productos')

    if request.method == 'POST':
        # Validar stock
        for item in carrito:
            if item['producto'].stock < item['cantidad']:
                messages.error(
                    request,
                    f"Stock insuficiente para '{item['producto'].nombre}'. "
                    f"Solo quedan {item['producto'].stock} unidades."
                )
                return redirect('ver_carrito')

        # Crear pedido
        pedido = Pedido.objects.create(usuario=request.user, total=carrito.total())

        # Crear items y descontar stock
        for item in carrito:
            producto = item['producto']
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                precio=item['precio'],
                cantidad=item['cantidad']
            )
            producto.stock -= item['cantidad']
            if producto.stock <= 0:
                producto.disponible = False
            producto.save()

        # Vaciar carrito
        del request.session['carrito']
        messages.success(request, f"Pedido #{pedido.id} creado. Procede con el pago.")
        return redirect('pago_transferencia', pedido_id=pedido.id)

    return render(request, 'tienda/checkout.html', {'carrito': carrito})


@login_required
def pago_transferencia(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if request.method == 'POST':
        pedido.referencia_transferencia = request.POST.get('referencia', '')
        if 'comprobante' in request.FILES:
            pedido.comprobante = request.FILES['comprobante']
        pedido.estado = 'pagado'
        pedido.save()
        messages.success(request, "Pago registrado. Verificaremos tu transferencia.")
        return redirect('confirmacion_pedido', pedido_id=pedido.id)

    return render(request, 'tienda/pago_transferencia.html', {'pedido': pedido})


@login_required
def confirmacion_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'tienda/confirmacion.html', {'pedido': pedido})


@login_required
def historial_pedidos(request):
    # Filtra los pedidos del usuario actual, ordenados del más reciente al más antiguo
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-creado')

    # Envía la lista al template
    return render(request, 'tienda/historial_pedidos.html', {'pedidos': pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    # get_object_or_404 busca el pedido por ID, PERO SOLO si pertenece al usuario
    # Si no es suyo, devuelve 404 (seguridad)
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    return render(request, 'tienda/detalle_pedido.html', {'pedido': pedido})


# ==================================================
# PERFIL DE USUARIO
# ==================================================
@login_required
def mi_perfil(request):
    """Editar datos personales y cambiar contraseña."""
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # --- Actualizar datos personales ---
        if accion == 'datos':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect('mi_perfil')

        # --- Cambiar contraseña ---
        elif accion == 'password':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña cambiada correctamente.")
                return redirect('mi_perfil')
            else:
                for error in form.errors.values():
                    messages.error(request, error.as_text())

    pedidos_usuario = Pedido.objects.filter(usuario=request.user).order_by('-creado')[:5]
    total_pedidos = Pedido.objects.filter(usuario=request.user).count()

    return render(request, 'tienda/mi_perfil.html', {
        'pedidos_usuario': pedidos_usuario,
        'total_pedidos': total_pedidos,
    })


# ==================================================
# ADMIN: PRODUCTOS (CRUD)
# ==================================================
@staff_member_required
def lista_admin(request):
    """Panel de administración con todos los productos."""
    productos = Producto.objects.all().order_by('-creado')

    # Estadísticas simples
    productos_sin_stock = productos.filter(stock=0).count()
    valor_inventario = productos.aggregate(
        total=Sum(F('precio') * F('stock'))
    )['total'] or 0

    return render(request, 'tienda/lista_admin.html', {
        'productos': productos,
        'productos_sin_stock': productos_sin_stock,
        'valor_inventario': valor_inventario,
    })


@staff_member_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto '{producto.nombre}' creado exitosamente.")
            return redirect('detalle_producto', pk=producto.pk)
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = ProductoForm()

    return render(request, 'tienda/crear_producto.html', {'form': form})


@staff_member_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado correctamente.")
            return redirect('detalle_producto', pk=producto.pk)
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'tienda/editar_producto.html', {
        'form': form,
        'producto': producto,
    })


@staff_member_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto '{nombre}' eliminado correctamente.")
        return redirect('lista_admin')

    return render(request, 'tienda/eliminar_producto.html', {'producto': producto})


# ==================================================
# ADMIN: CATEGORÍAS (CRUD)
# ==================================================
@staff_member_required
def lista_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'tienda/lista_categorias.html', {'categorias': categorias})


@staff_member_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f"Categoría '{categoria.nombre}' creada correctamente.")
            return redirect('lista_categorias')
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = CategoriaForm()
    return render(request, 'tienda/crear_categoria.html', {'form': form})


@staff_member_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoría '{categoria.nombre}' actualizada.")
            return redirect('lista_categorias')
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'tienda/crear_categoria.html', {
        'form': form,
        'categoria': categoria,
    })


@staff_member_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    # Bloquear si tiene productos asociados
    if categoria.productos.exists():
        messages.error(
            request,
            f"No puedes eliminar '{categoria.nombre}' porque tiene "
            f"{categoria.productos.count()} producto(s) asociado(s). "
            "Primero muévelos a otra categoría o elimínalos."
        )
        return redirect('lista_categorias')

    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f"Categoría '{nombre}' eliminada.")
        return redirect('lista_categorias')

    return render(request, 'tienda/eliminar_categoria.html', {'categoria': categoria})

# ==================================================
# LISTA ADMIN
# ==================================================

@staff_member_required
def lista_admin(request):
    """Panel de administración con todos los productos y estadísticas."""
    productos = Producto.objects.all().order_by('-creado')

    # Estadísticas
    total_productos = productos.count()
    productos_disponibles = productos.filter(disponible=True, stock__gt=0).count()
    productos_sin_stock = productos.filter(stock=0).count()
    productos_stock_bajo = productos.filter(stock__gt=0, stock__lte=5).count()

    valor_inventario = productos.aggregate(
        total=Sum(F('precio') * F('stock'))
    )['total'] or 0

    # Ventas (si tienes pedidos)
    from datetime import date, timedelta
    hoy = date.today()
    ventas_hoy = Pedido.objects.filter(
        creado__date=hoy,
        estado__in=['pagado', 'enviado', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0

    # Productos agotados
    productos_agotados = productos.filter(stock=0)

    return render(request, 'tienda/lista_admin.html', {
        'productos': productos,
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_agotados': productos_agotados,
        'valor_inventario': valor_inventario,
        'ventas_hoy': ventas_hoy,
    })

def detalle_producto(request, pk):
    # Busca el producto por su ID, si no existe da error 404
    producto = get_object_or_404(Producto, pk=pk)

    # Busca hasta 4 productos de la MISMA categoría (excluyendo el actual)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        disponible=True
    ).exclude(pk=producto.pk)[:4]

    # Envía el producto y los relacionados al template
    return render(request, 'tienda/detalle.html', {
        'producto': producto,
        'relacionados': relacionados,
    })

@login_required
def checkout(request):
    carrito = Carrito(request)

    if len(carrito) == 0:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('lista_productos')

    if request.method == 'POST':
        # Obtener método de pago elegido
        metodo = request.POST.get('metodo_pago', 'transferencia')

        # Validar stock
        for item in carrito:
            if item['producto'].stock < item['cantidad']:
                messages.error(request, f"Stock insuficiente para '{item['producto'].nombre}'.")
                return redirect('ver_carrito')

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=carrito.total(),
            metodo_pago=metodo,
        )

        # Crear items y descontar stock
        for item in carrito:
            producto = item['producto']
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                precio=item['precio'],
                cantidad=item['cantidad']
            )
            producto.stock -= item['cantidad']
            if producto.stock <= 0:
                producto.disponible = False
            producto.save()

        del request.session['carrito']

        # Redirigir según método elegido
        if metodo == 'transferencia':
            return redirect('pago_transferencia', pedido_id=pedido.id)
        elif metodo == 'mercadopago':
            return redirect('pago_mercadopago', pedido_id=pedido.id)
        elif metodo == 'binance':
            return redirect('pago_binance', pedido_id=pedido.id)
        elif metodo == 'zelle':
            return redirect('pago_zelle', pedido_id=pedido.id)

    return render(request, 'tienda/checkout.html', {'carrito': carrito})
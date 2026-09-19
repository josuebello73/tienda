from django.db import models
from django.contrib.auth.models import User


# Create your models here.



class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado']

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de pago'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]

    METODOS_PAGO = [
        ('transferencia', 'Transferencia bancaria'),
        ('mercadopago', 'MercadoPago'),
        ('binance', 'Binance Pay / USDT'),
        ('zelle', 'Zelle'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ⬇️ CAMPO NUEVO
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='transferencia'
    )

    referencia_transferencia = models.CharField(max_length=100, blank=True)
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-creado']

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField()

    class Meta:
        verbose_name = "Item del pedido"
        verbose_name_plural = "Items del pedido"

    def subtotal(self):
        return self.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad}× {self.producto.nombre if self.producto else 'Producto eliminado'}"

def checkout(request):
    carrito = Carrito(request)
    if request.method == 'POST':
        pedido = Pedido.objects.create(usuario=request.user, total=carrito.total())
        for item in carrito:
            producto = item['producto']
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                precio=item['precio'],
                cantidad=item['cantidad']
            )
            # Descontar stock
            producto.stock -= item['cantidad']
            if producto.stock <= 0:
                producto.disponible = False
            producto.save()
        # Vaciar carrito
        del request.session['carrito']
        return redirect('pago_transferencia', pedido_id=pedido.id)
    return render(request, 'tienda/checkout.html', {'carrito': carrito})

def pago_transferencia(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    if request.method == 'POST':
        pedido.referencia_transferencia = request.POST.get('referencia', '')
        if 'comprobante' in request.FILES:
            pedido.comprobante = request.FILES['comprobante']
        pedido.estado = 'pagado'  # Marcar como pagado pendiente de verificación
        pedido.save()
        return redirect('confirmacion_pedido', pedido_id=pedido.id)
    return render(request, 'tienda/pago_transferencia.html', {'pedido': pedido})
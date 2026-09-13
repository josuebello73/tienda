from decimal import Decimal
from .models import Producto

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {'cantidad': 0, 'precio': str(producto.precio)}
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def guardar(self):
        self.session.modified = True

    def __iter__(self):
        ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=ids)
        carrito = self.carrito.copy()
        for p in productos:
            carrito[str(p.id)]['producto'] = p
        for item in carrito.values():
            item['precio'] = Decimal(item['precio'])
            item['total'] = item['precio'] * item['cantidad']
            yield item

    def total(self):
        return sum(item['total'] for item in self)

def __len__(self):
    return sum(item['cantidad'] for item in self.carrito.values())
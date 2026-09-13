from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),

    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),

    # Pedidos
    path('checkout/', views.checkout, name='checkout'),
    path('pago/<int:pedido_id>/', views.pago_transferencia, name='pago_transferencia'),
    path('confirmacion/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('mis-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),

    # Admin CRUD
    path('admin-productos/', views.lista_admin, name='lista_admin'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    # Auth
    path('logout/', views.cerrar_sesion, name='logout'),

    #
# ==================== USUARIO ====================
    path('mis-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('logout/', views.cerrar_sesion, name='logout'),

# ==================== CATEGORÍAS (ADMIN) ====================
path('categorias/', views.lista_categorias, name='lista_categorias'),
path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),

    
]
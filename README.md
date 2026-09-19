# Mi Tienda

Ecommerce desarrollado con Django para gestionar catálogo de productos, carrito de compras, pedidos, administración de productos y perfil de usuario con foto de perfil.

## Descripción general

Este proyecto es una tienda online básica pero funcional, pensada para aprender y extender con nuevas funcionalidades. Permite:

- Ver productos y filtrar por categoría, precio y búsqueda.
- Agregar productos al carrito.
- Realizar checkout y registrar pago por transferencia.
- Consultar historial de pedidos.
- Registrar e iniciar sesión como usuario.
- Editar perfil personal, cambiar contraseña y subir o eliminar foto de perfil.
- Gestionar productos y categorías como administrador.

## Tecnologías utilizadas

- Python 3
- Django 6.1.1
- SQLite
- HTML, CSS, JavaScript
- Bootstrap-like custom CSS
- Django templates

## Estructura del proyecto

El proyecto se organiza de la siguiente forma:

```text
Curso/
├── .git/
├── .gitignore
├── venv/
├── tienda/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── tienda/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── cart.py
│   │   ├── forms.py
│   │   ├── manage.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── static/
│   │   ├── templates/
│   │   └── media/
│   ├── requirements.txt
│   └── db.sqlite3
└── README.md
```

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.10 o superior
- pip
- Git
- Entorno virtual recomendado

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/josuebello73/tienda.git
cd tienda
```

2. Crea y activa un entorno virtual:

En Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución del proyecto

La aplicación Django real está dentro de la carpeta anidada `tienda/tienda` y se debe ejecutar desde ahí usando el entorno virtual.

Desde la raíz del repositorio:

```powershell
Set-Location 'C:\Users\Admin\OneDrive\Escritorio\Curso'
.\venv\Scripts\python.exe .\tienda\tienda\manage.py runserver
```

Luego abre en el navegador:

```text
http://127.0.0.1:8000/
```

## Base de datos

El proyecto usa SQLite por defecto. La base de datos se encuentra en:

```text
C:\Users\Admin\OneDrive\Escritorio\Curso\tienda\tienda\db.sqlite3
```

Si necesitas crear nuevas migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Variables y configuración

El archivo principal de configuración está en:

- `tienda/tienda/config/settings.py`

Aquí se configuran, entre otros aspectos:

- aplicación instalada
- configuración de base de datos
- rutas de archivos estáticos
- rutas de media
- configuración de login/logout
- configuración de email para recuperación de contraseña

La media y los archivos subidos por usuarios se guardan en:

```text
tienda/tienda/media/
```

## Funcionalidades principales

### 1. Catálogo de productos

- Lista productos con filtros por categoría, precio y texto.
- Ordenación por precio o novedades.
- Vista de detalle del producto.

### 2. Carrito de compras

- Agregar productos al carrito.
- Modificar cantidades.
- Eliminar artículos.
- Cálculo del total.

### 3. Checkout y pagos

- Pedido del usuario.
- Registro de referencia de pago.
- Subida de comprobante de pago.
- Estados por pedido.

### 4. Autenticación y perfil

- Registro de usuarios.
- Inicio y cierre de sesión.
- Cambio de contraseña.
- Edición de nombre, apellido y correo.
- Subida de foto de perfil.

### 5. Foto de perfil

La funcionalidad de avatar está implementada con el modelo `Perfil` y un campo `ImageField`.

Características:

- Si el usuario no sube foto, se usa un avatar por defecto con icono de usuario.
- Si el usuario sube una imagen, se reemplaza el valor por defecto.
- La imagen se guarda en la carpeta `avatares/` dentro de `media/`.
- El avatar se muestra tanto en el perfil como en el encabezado principal.

### 6. Administración

El administrador puede:

- Crear, editar y eliminar productos.
- Crear, editar y eliminar categorías.
- Revisar pedidos realizados por clientes.

## Modelos principales

### `Perfil`

Representa el perfil del usuario y su foto de perfil.

```python
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True)
```

### `Producto`

Representa cada producto del catálogo.

### `Categoria`

Agrupa productos por tipo o sección.

### `Pedido`

Guarda la compra con su estado y total.

### `PedidoItem`

Cada línea del pedido asociada a un producto concreto.

## Archivos clave

- `tienda/tienda/models.py`: modelos de la app.
- `tienda/tienda/views.py`: lógica de la aplicación.
- `tienda/tienda/urls.py`: rutas de la app.
- `tienda/tienda/forms.py`: formularios de registro y gestión.
- `tienda/tienda/templates/tienda/`: plantillas HTML.
- `tienda/tienda/static/css/`: estilos de la interfaz.

## Variables de entorno

En este proyecto no se usa un archivo `.env` todavía. La configuración actual es local y de desarrollo.

Si quieres desplegarlo en producción, es recomendable:

- cambiar `DEBUG` a `False`
- configurar `ALLOWED_HOSTS`
- ocultar `SECRET_KEY`
- usar un servidor de producción
- configurar email real
- usar base de datos distinta a SQLite

## Recuperación de contraseña

La configuración actual usa email en consola, por lo que los mensajes se muestran en la terminal en lugar de enviarse por correo real.

Configuración activa:

```python
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    }
}
```

## Uso típico del sistema

### Como cliente

1. Crear cuenta.
2. Iniciar sesión.
3. Explorar catálogo.
4. Agregar productos al carrito.
5. Finalizar compra.
6. Comprobar pedidos y perfil.

### Como administrador

1. Entrar al panel de administración.
2. Crear categorías.
3. Agregar productos.
4. Revisar pedidos.
5. Actualizar stock y disponibilidad.

## Limpieza y estructura

Durante el desarrollo se detectaron copias duplicadas del proyecto en rutas distintas. Se dejó la estructura activa en la ruta:

```text
C:\Users\Admin\OneDrive\Escritorio\Curso\tienda\tienda
```

Esto evita conflictos de rutas y mantiene el proyecto consistente.

## Estado actual

El proyecto se encuentra validado con Django mediante:

```powershell
.\venv\Scripts\python.exe .\tienda\tienda\manage.py check
```

Resultado esperado:

```text
System check identified no issues (0 silenced).
```

## Próximos pasos recomendados

- Mejorar diseño responsive para móvil.
- Añadir paginación y filtros avanzados.
- Integrar pasarelas reales de pago.
- Añadir validación de stock más robusta.
- Mejorar sistema de fotos de perfil con redimensionado automático.
- Preparar despliegue en producción.

## Licencia

Este proyecto se entrega con fines educativos y de desarrollo. Ajusta la licencia según lo requieras antes de publicarlo o distribuirlo.

## Autor

Proyecto desarrollado para aprendizaje y práctica de Django con tienda online y gestión de perfil de usuario.

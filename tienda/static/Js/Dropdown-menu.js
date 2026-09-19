/**
 * Controla el dropdown del usuario en el header.
 * - Al pasar el mouse sobre .user-menu → se muestra el dropdown
 * - Al hacer clic sobre .user-menu → también lo abre/cierra
 * - Al hacer clic fuera → se cierra
 */
document.addEventListener('DOMContentLoaded', function () {
    const userMenu = document.querySelector('.user-menu');
    const userDropdown = document.querySelector('.user-dropdown');

    if (!userMenu || !userDropdown) return;

    // Forzar que el dropdown esté oculto al cargar la página
    userDropdown.style.display = 'none';

    // Al hacer clic sobre el nombre → toggle
    userMenu.addEventListener('click', function (e) {
        e.stopPropagation();
        const visible = userDropdown.style.display === 'block';
        userDropdown.style.display = visible ? 'none' : 'block';
    });

    // Al hacer clic fuera → cerrar
    document.addEventListener('click', function () {
        userDropdown.style.display = 'none';
    });

    // Al hacer clic dentro del dropdown → no cerrar
    userDropdown.addEventListener('click', function (e) {
        e.stopPropagation();
    });
});
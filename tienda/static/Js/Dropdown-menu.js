/** Controla el dropdown del usuario al hacer clic. */
document.addEventListener('DOMContentLoaded', function () {
    const userMenu = document.querySelector('.user-menu');
    const userName = document.querySelector('.user-name');
    const userDropdown = document.querySelector('.user-dropdown');

    if (!userMenu || !userName || !userDropdown) return;

    userName.setAttribute('role', 'button');
    userName.setAttribute('tabindex', '0');
    userName.setAttribute('aria-expanded', 'false');

    function closeMenu() {
        userMenu.classList.remove('is-open');
        userName.setAttribute('aria-expanded', 'false');
    }

    function toggleMenu(e) {
        e.stopPropagation();
        const isOpen = userMenu.classList.toggle('is-open');
        userName.setAttribute('aria-expanded', String(isOpen));
    }

    userName.addEventListener('click', toggleMenu);
    userName.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleMenu(e);
        }
    });

    document.addEventListener('click', function () {
        closeMenu();
    });

    userDropdown.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
});
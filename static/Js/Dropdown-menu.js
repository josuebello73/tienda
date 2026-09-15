document.addEventListener('DOMContentLoaded', () => {

    const boton = document.querySelector('.user-menu');
    const menu = document.querySelector('.user-dropdown');

    if (boton && menu) {
        boton.addEventListener('click', (event) => {
            menu.classList.toggle('active');
            event.stopPropagation();
        });
    }

    window.addEventListener('click', (event) => {
        if (!menu.contains(event.target) && !boton.contains(event.target)) {
            menu.classList.remove('active');
        }
    }); 
});
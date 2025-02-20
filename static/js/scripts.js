document.addEventListener('DOMContentLoaded', function () {
    const menuIcon = document.getElementById('menu-icon');
    const sidebar = document.getElementById('sidebar');

    // Mostrar/ocultar la sidebar al hacer clic en el ícono de menú
    menuIcon.addEventListener('click', function (event) {
        event.stopPropagation(); // Evita que el evento se propague
        sidebar.classList.toggle('active');
    });

    // Ocultar la sidebar al hacer clic fuera de ella
    document.addEventListener('click', function (event) {
        if (!sidebar.contains(event.target) && !menuIcon.contains(event.target)) {
            sidebar.classList.remove('active');
        }
    });
});

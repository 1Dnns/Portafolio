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



document.addEventListener('DOMContentLoaded', function () {
    const professions = [
        "Ingeniero Físico",
        "Data Science",
        "Técnico en Mecánica Automotriz y Autotrónica",
    ];

    const professionElement = document.querySelector('.lead');
    let index = 0;

    function animateProfessions() {
        professionElement.textContent = professions[index];
        professionElement.classList.remove('hidden');
        professionElement.style.animation = 'typing 2s steps(40, end), blink-caret 0.75s step-end infinite';

        setTimeout(() => {
            professionElement.style.animation = 'erase 1s steps(40, end), blink-caret 0.75s step-end infinite'; // Animación de borrado
            setTimeout(() => {
                professionElement.classList.add('hidden');
                index = (index + 1) % professions.length;
                setTimeout(animateProfessions, 500); // Tiempo entre profesiones
            }, 1000); // Duración de la animación de borrado
        }, 3000); // Duración de la animación de escritura + tiempo que permanece
    }

    animateProfessions();
});
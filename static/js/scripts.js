document.addEventListener('DOMContentLoaded', function() {
    // Agregar funcionalidad de desplazamiento a las secciones de proyectos
    document.querySelectorAll('.row.flex-nowrap').forEach(row => {
        row.addEventListener('wheel', (e) => {
            if (e.deltaY > 0) {
                row.scrollLeft += 100; // Ajusta la cantidad de desplazamiento
            } else {
                row.scrollLeft -= 100; // Ajusta la cantidad de desplazamiento
            }
        });
    });
});
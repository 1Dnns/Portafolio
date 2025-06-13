# 🌐 Portafolio Personal – Denis Bravo

Este es mi portafolio profesional desarrollado con **Django**, donde presento mis proyectos, experiencia y habilidades en ciencia de datos, machine learning y desarrollo web.

El sitio cuenta con una interfaz limpia, adaptable y funcional, diseñada para destacar tanto el contenido como la estructura técnica del backend.

> 🔗 **Versión en línea:** [https://tu-dominio-aqui.com](https://tu-dominio-aqui.com) _(en proceso de despliegue)_

---

## 🧰 Tecnologías utilizadas

- **Python** (versión 3.10.12)
- **Django** (versión 5.1.3)
- **MySQL** – Base de datos relacional
- **Railway** – Plataforma para alojar bases de datos en la nube
- **Bootstrap** – Framework CSS
- **HTML / CSS / JavaScript**
- **Render** – (para el despliegue de la app web)
- **Git / GitHub** – Control de versiones

---

## 📄 Secciones del sitio

- **Inicio:** presentación general
- **Perfil:** resumen profesional
- **Habilidades:** lenguajes de programación, tecnologías y herramientas
- **Formación:** antecedentes académicos
- **Experiencia:** historial laboral relevante
- **Proyectos:** trabajos destacados, incluyendo:
  - Dashboard de diputados de Chile (con visualizaciones interactivas)
  - Proyectos de machine learning con técnicas de regresión
  - Scripts de scraping automatizado
- **Contacto:** formulario para comunicación directa

---

## 🚀 Instrucciones para correr el proyecto localmente

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/portafolio.git
cd portafolio

# 2. Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura tus variables de entorno (por ejemplo, en un archivo .env)

# 5. Ejecuta las migraciones y levanta el servidor
python manage.py migrate
python manage.py runserver

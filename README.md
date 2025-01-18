# TFG Laura Maria Garcia Suarez

Creado por Laura María García Suárez.

Revisado por Iván Cantador Gutiérrez

## Introducción

A continuación, encontrará información acerca del TFG "Sistema de evaluación de algoritmos de recomendación (Juegos de Mesa)".

## TO-DOs

- [X] Crear maquetado inicial del proyecto (*)
- [X] Crear versión inicial de la página web (*)
- [X] Probar a subir una página web usando Docker, Kubernetes y Minikube. (02/10/24)
- [X] Modificar página de login (02/10/24)
- [X] Arreglar navbar general (expansión y reducción) (28/10/24)
- [X] Modificar página de registro (06/10/24)
- [X] Comprobar la validación de la contraseña (10/10/24)
- [X] Crear página de preferencias (13/10/24)
- [X] Dar la opción de mostrar más información de los juegos (16/10/2024)
- [X] Modificar página de home del usuario (17/10/24)
- [X] Cambiar base de datos de sqlite (10/10/24)
- [ ] Mostrar errores del registro
- [X] Cargar BD de BGG (13/10/24)
- [ ] Comprobar CSS inutilizable
- [ ] Comprimir HTML
- [X] Hacer uso de los datos contenidos en BGG(17/11/2024)
- [ ] Obtener las preferencias y guardarlas en una BD
- [X] Poner todo en inglés (26/10/2024)
- [X] Modificar páginas de recomendaciones (24/10/24 y 26/10/24)
- [X] Obtener los juegos recomendados gustados en views.py (28/10/24)
- [X] Conseguir traducción de la página (17/11/2024)
- [ ] Comprobar el error que está ocasionando algunos juegos en la página de preferencias
- [ ] Mostrar mensaje de error de que no existe el usuario (pag. inicial)
- [X] Género en registro
- [ ] Revisar traducciones de todas las páginas
- [ ] Hacer boton logout y si accede a home y esta login, que vaya directamente a user-home
- [ ] Poner todos los label de register -> valido
- [X] Comprobar forloop de questionnarie.html (15/01/2025)
- [ ] Comprobar muchas questions en questionnarie
- [ ] Violacion de segmento?
- [ ] Arreglar vulnerabilidades de github
- [ ] Cambiar color checkbox

### Evaluación del participante

- Cuanto le interesa el producto o juego?
- Que tan probable es de que lo compre/recomiende?
- Se ajusta a tus preferencias?
- Te gustaría que tuviera más opciones (dificultad, opciones de personalización, modos de juego...)?
- Cuál fue el principal factor que influye en tu decision de compra/recomendacion? Precio, calidad, características, popularidad, recomendaciones de otros usuarios...
- 

## Base de Datos

### PostgreSQL (La más recomendada)

   Por qué elegirla:

Fiabilidad: Es una base de datos muy robusta y ampliamente utilizada en producción. Ofrece una excelente integridad de datos y es altamente escalable.
Compatibilidad con Django: Django tiene un soporte nativo muy completo para PostgreSQL. De hecho, muchas características avanzadas de Django (como la búsqueda full-text o los campos JSON) están optimizadas para PostgreSQL.
Soporte de Docker: Hay imágenes oficiales de PostgreSQL disponibles en Docker Hub, lo que facilita la integración en tu contenedor Docker.
Seguridad: PostgreSQL tiene características avanzadas de autenticación y permisos que lo hacen seguro para manejar datos sensibles como las credenciales de los usuarios.

Ventajas:

Escalable, confiable y robusta para producción.
Compatible con la mayoría de los servicios en la nube (AWS RDS, Google Cloud SQL).
Soporte avanzado de transacciones, integridad referencial y características específicas de PostgreSQL.
Desventajas:

Requiere un poco más de configuración inicial en comparación con SQLite o MySQL.

#### YAML para futuro con Docker

version: '3'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:

### SQlite

Desventajas:
No escalable: No es adecuado para aplicaciones que necesitan escalar. SQLite no maneja bien las cargas de múltiples usuarios simultáneos y grandes volúmenes de datos.
No recomendado para producción: Aunque es fácil de usar en desarrollo, para producción deberías cambiar a una base de datos más robusta como PostgreSQL o MySQL.

composer require vlucas/phpdotenv

## Problemas

No funcionó gitlab desde 07/10/24 hasta (15/10/24???).

## Palabras clave

Un meeple es una figura o ficha que se utiliza en muchos juegos de mesa, especialmente en los juegos de estrategia y de construcción. La palabra "meeple" es una combinación de "my" y "people" (mi gente), y se refiere a los pequeños personajes de madera, plástico o cartón que representan a los jugadores en el juego.

Preguntas que pueden hacerme

- por que django y no java pejem
- porq postgres
- 

## Bibliografía importante

-> Elección de BD: https://dev.to/rupesh_mishra/connecting-cloud-hosted-postgresql-to-django-a-comprehensive-guide-5cl1#:~:text=Django%2C%20by%20default%2C%20uses%20SQLite,that's%20often%20used%20in%20production.

-> Elección de BD: https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison

-> Traducción de las páginas: https://www.freecodecamp.org/news/localize-django-app/

-> Datos de juegos: https://www.w3schools.com/xml/ajax_database.asp

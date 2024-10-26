# TFG Laura Maria Garcia Suarez

Copia de seguridad de mi TFG por errores de gitlab

Creado por Laura María García Suárez.

Revisado por Iván Cantador Gutiérrez

## Introducción

A continuación, encontrará información acerca del TFG "Sistema de evaluación de algoritmos de recomendación (Juegos de Mesa)".

## TO-DOs

- [X] Crear maquetado inicial del proyecto (*)
- [X] Crear versión inicial de la página web (*)
- [X] Probar a subir una página web usando Docker, Kubernetes y Minikube. (02/10/24)
- [X] Modificar página de login (02/10/24)
- [ ] Arreglar navbar general (expansión y reducción)
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
- [ ] Hacer uso de los datos contenidos en BGG
- [ ] obtener las preferencias y guardarlas en una BD
- [ ] Poner todo en inglés
- [X] Modificar páginas de recomendaciones (24/10/24 y 26/10/24)

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

## Problemas

No funcionó gitlab desde 07/10/24 hasta (15/10/24???).

## Palabras clave

Un meeple es una figura o ficha que se utiliza en muchos juegos de mesa, especialmente en los juegos de estrategia y de construcción. La palabra "meeple" es una combinación de "my" y "people" (mi gente), y se refiere a los pequeños personajes de madera, plástico o cartón que representan a los jugadores en el juego.

## Bibliografía importante

-> Elección de BD: https://dev.to/rupesh_mishra/connecting-cloud-hosted-postgresql-to-django-a-comprehensive-guide-5cl1#:~:text=Django%2C%20by%20default%2C%20uses%20SQLite,that's%20often%20used%20in%20production.

-> Elección de BD: https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison

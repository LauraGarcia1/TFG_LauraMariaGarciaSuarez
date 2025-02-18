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
- [X] Cargar BD de BGG (13/10/24)
- [X] Hacer uso de los datos contenidos en BGG(17/11/2024)
- [X] Obtener las preferencias y guardarlas en una BD (05/01/2025)
- [X] Poner todo en inglés (26/10/2024)
- [X] Modificar páginas de recomendaciones (24/10/24 y 26/10/24)
- [X] Obtener los juegos recomendados gustados en views.py (28/10/24)
- [X] Conseguir traducción de la página (17/11/2024)
- [X] Género en registro
- [X] Hacer boton logout y si accede a home y esta login, que vaya directamente a user-home (27/01/2025)
- [X] Comprobar forloop de questionnarie.html (15/01/2025)
- [X] Arreglar vulnerabilidades de github (18/01/2025)
- [X] Cambiar color checkbox (21/01/2025)
- [X] Cambio de idioma de las questions (23/01/2025)
- [X] Poner todos los label de register -> valido (16/02/2025)
- [X] Comprobar muchas questions en questionnarie (16/02/2025)
- [X] Cambiar etiquetas de roles de usuario (16/02/2025)
- [X] un creador no puede tener preferencias (17/02/2025)
- [X] Eliminacion de objetos en la creación de cuestionario (17/02/2025)
- [ ] Eliminacion de objetos en la edición de cuestionario
- [ ] Página de creación de algoritmos. Cómo lo uso?
- [ ] Probar cambios questionnarie y language
- [ ] Hacer validación de la página de creación de questionarios
  - [ ] Que haya datos en el cuestionario, secciones, preguntas y choices (este último si fuese necesario)
  - [ ] Que tenga secciones
  - [ ] Que las secciones tengan preguntas
  - [ ] Que las preguntas tengan choices si es necesario
  - [ ] El algoritmo usado para el cuestionario
- [ ] Revisar traducciones de todas las páginas
- [ ] Documentar correctamente el código
- [ ] Comprobar el error que está ocasionando algunos juegos en la página de preferencias
- [ ] Violacion de segmento?
- [ ] Mostrar mensaje de error de que no existe el usuario (pag. inicial)
- [ ] Comprimir HTML
- [ ] Limpiar código que no se use
- [ ] Comprobar CSS inutilizable
- [ ] Mostrar errores del registro

### Evaluación del participante

- Cuanto le interesa el producto o juego?
- Que tan probable es de que lo compre/recomiende?
- Se ajusta a tus preferencias?
- Te gustaría que tuviera más opciones (dificultad, opciones de personalización, modos de juego...)?
- Cuál fue el principal factor que influye en tu decision de compra/recomendacion? Precio, calidad, características, popularidad, recomendaciones de otros usuarios...

## Caso de uso

**Ejemplo de una evaluación**

Supongamos que:

1. **El usuario** : Carlos completa un cuestionario inicial sobre sus preferencias en juegos de mesa (por ejemplo, le gustan los juegos estratégicos con duración media y adecuados para 4 personas).
2. **El sistema de recomendación** : Basado en sus respuestas, recomienda 5 juegos.

Los juegos recomendados son:

* **Juego A: Catan**
* **Juego B: Azul**
* **Juego C: Carcassonne**
* **Juego D: Dixit**
* **Juego E: Pandemic**

---

### **El proceso de evaluación**

Carlos evalúa cada uno de los juegos recomendados respondiendo a las preguntas proporcionadas. La **evaluación** para **Juego A: Catan** podría incluir lo siguiente:

1. **Cuánto le interesa el producto o juego?**
   * Respuesta: **5/5** (Muy interesado).
2. **Qué tan probable es que lo compre/recomiende?**
   * Respuesta: **4/5** (Probablemente lo compre y lo recomiende).
3. **¿Se ajusta a tus preferencias?**
   * Respuesta:  **Sí** .
4. **¿Te gustaría que tuviera más opciones (dificultad, opciones de personalización, modos de juego...)?**
   * Respuesta:  **Sí, modos de juego adicionales** .
5. **¿Cuál fue el principal factor que influye en tu decisión de compra/recomendación?**
   * Respuesta:  **Calidad y características** .

---

### **Qué hace la evaluación?**

1. **Recopila datos sobre cada recomendación:**

   * Para  **Catan** , sabemos que Carlos está muy interesado, lo considera relevante y le gustaría más modos de juego.
   * Además, sabemos que la calidad y las características son lo que más valora.
2. **Analiza el rendimiento del sistema:**

   * Si Carlos evalúa **Juego A** con puntajes altos y lo considera relevante, significa que el sistema acertó.
   * Por otro lado, si **Juego D: Dixit** tiene respuestas como "no se ajusta a mis preferencias" o "poco probable que lo compre", el sistema debe mejorar.
3. **Retroalimenta al algoritmo de recomendación:**

   * Los datos de evaluación (interés, relevancia, factores de compra) ayudan al algoritmo a entender mejor las preferencias de Carlos y de otros usuarios similares.
   * Por ejemplo, si muchos usuarios con preferencias estratégicas como Carlos prefieren juegos como **Catan** y  **Pandemic** , el sistema puede priorizar esos juegos en futuras recomendaciones.
4. **Permite análisis posteriores:**

   * A nivel de plataforma, puedes identificar tendencias como:
     * ¿Cuáles son los factores más importantes para los usuarios (precio, calidad, etc.)?
     * ¿Qué juegos tienen las mejores evaluaciones?
     * ¿Qué juegos necesitan mejoras (por ejemplo, en personalización)?

## Análisis de requisitos

1. La plataforma debe poder presentar varios estudios al participante.
2. La plataforma debe poder usar algoritmos de recomendación.
3. Los participantes deben de ser capaces de registrarse e iniciar sesión en la plataforma.
4. Los usuarios deben poder escoger entre 2 roles, el rol de Creador y el rol de Participante.
5. Los Creadores deben poder añadir nuevos estudios.
6. Los Creadores deben poder añadir preguntas para las recomendaciones.
7. Los Participantes deben poder responder las preguntas de forma individual para cada juego recomendado por el Algoritmo.
8. Los Creadores deben poder hacer uso de distintos algoritmos de Recomendación.
9. La plataforma debe poder traducir todo el contenido en Español o Inglés.
10. La plataforma debe guardar las respuestas del Evaluado en la base de datos.
11. Los Participantes, una vez registrados, deberán introducir una serie de preferencias de juegos que le puedan interesar.

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

- No funcionó gitlab desde 07/10/24 hasta (15/10/24???).
- Disponibilidad de cada uno

## Mejoras

- Control de rol creador de la aplicación
- El usuario puede modificar sus datos
- El perfil se puede definir para cada experimento
- Que se haga una comprobación de que los cuestionarios añadidos estén en el idioma seleccionado

## Palabras clave

Un meeple es una figura o ficha que se utiliza en muchos juegos de mesa, especialmente en los juegos de estrategia y de construcción. La palabra "meeple" es una combinación de "my" y "people" (mi gente), y se refiere a los pequeños personajes de madera, plástico o cartón que representan a los jugadores en el juego.

## Preguntas que pueden hacerme

- ¿Por que django y no java pejem?
- ¿Por que postgres en vez de otra BD?
- ¿Que vulns tuve que arreglar? (eliminar?)
- ¿Por que no he usado nested_forms? Resp: mucha complejidad para lo que puede hacer

## Bibliografía importante

-> Elección de BD: https://dev.to/rupesh_mishra/connecting-cloud-hosted-postgresql-to-django-a-comprehensive-guide-5cl1#:~:text=Django%2C%20by%20default%2C%20uses%20SQLite,that's%20often%20used%20in%20production.

-> Elección de BD: https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison

-> Traducción de las páginas: https://www.freecodecamp.org/news/localize-django-app/

-> Datos de juegos: https://www.w3schools.com/xml/ajax_database.asp

-> Django: https://www.djangoproject.com/start/

-> Inline Factory -> https://micropyramid.com/blog/how-to-use-nested-formsets-in-django

-> https://github.com/mbertheau/jquery.django-formset-example/tree/master

-> Herramientas para visualizar bases de datos
   https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools
   Dbeaver
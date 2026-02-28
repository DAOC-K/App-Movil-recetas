# App Móvil de Recetas 

Aplicación móvil diseñada para la gestión de recetas de cocina. Permite a los usuarios crear una comunidad culinaria, publicar platos, interactuar y optimizar sus idas al supermercado automatizando las listas de ingredientes.

##  Características Principales
* **Autenticación:** Sistema seguro de inicio de sesión y registro de usuarios.
* **Exploración de Recetas:** Interfaz gráfica para visualizar platillos con fotografías, descripción detallada e instrucciones paso a paso.
* **Interacción Social:** Sistema de comentarios integrado por cada receta y capacidad para que los usuarios suban fotos de sus resultados.
* **Asistente de Compras:** Módulo que extrae los ingredientes de las recetas seleccionadas y genera una lista de compras interactiva.

##  Stack Tecnológico Definido
* **Frontend (App Móvil):** React Native (Permite compilar para Android y iOS desde una misma base de código).
* **Backend (API REST):** Python (Gestión ágil de rutas y lógica de negocio).
* **Base de Datos:** MySQL (Gestión relacional garantizando la integridad entre usuarios, ingredientes y recetas).
* **Almacenamiento de Archivos:** Cloud Storage (AWS S3 / Firebase) para alojar las fotografías de la comunidad.

##  Modelo de Datos Estructural
El sistema se sostiene sobre una arquitectura relacional sólida con las siguientes entidades principales:
1. `Usuarios` (Credenciales y perfiles)
2. `Recetas` (Información principal del plato y URL de la imagen)
3. `Ingredientes` (Cantidades exactas vinculadas a cada receta)
4. `Comentarios` (Registro de interacciones vinculando al usuario y la receta)

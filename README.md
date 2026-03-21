# App Móvil de Recetas 

Aplicación móvil diseñada para la gestión de recetas de cocina. Permite a los usuarios crear una comunidad culinaria, publicar platos, interactuar y optimizar sus idas al supermercado automatizando las listas de ingredientes.

##  Características Principales
## 🚀 Características Principales y Diferenciadores
* **Generador "Chef IA":** Integración con Inteligencia Artificial para sugerir recetas instantáneas basadas en los ingredientes exactos que el usuario tiene disponibles en casa, evitando el desperdicio de alimentos.
* **Modo Supermercado Offline:** La lista de compras cuenta con persistencia de datos local (caché/almacenamiento interno). El usuario puede tachar sus ingredientes en el supermercado sin depender de una conexión a internet, sincronizándose con la base de datos al recuperar la señal.
* **Exploración e Interacción:** Feed dinámico de recetas con sistema de comentarios integrado y carga de fotografías reales por parte de la comunidad.
* **Autenticación Segura:** Sistema de inicio de sesión y registro de usuarios para mantener el historial de recetas y listas de compras personalizadas.

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


## 🎨 Diseños y Mockups (UI/UX)
Los diseños iniciales y la experiencia de usuario fueron creados en Figma. 
[🔗 Haz clic aquí para ver los mockups interactivos](https://www.figma.com/make/B8pM3vUeaqL8xzBWVSrKpW/Aplicaci%C3%B3n-de-recetas-m%C3%B3viles?t=EFOURGrKjQYYZjJg-1&preview-route=%2Fapp)


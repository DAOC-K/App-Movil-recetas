-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS cook_and_share;
USE cook_and_share;

-- Tabla 1: Usuarios (Autenticación)
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla 2: Recetas
CREATE TABLE Recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    instructions TEXT NOT NULL,
    image_url VARCHAR(255), -- URL de la foto en la nube
    is_ai_generated BOOLEAN DEFAULT FALSE, -- Identifica si la hizo el "Chef IA"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Tabla 3: Ingredientes (Vinculados a una receta)
CREATE TABLE Ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    quantity VARCHAR(50),
    FOREIGN KEY (recipe_id) REFERENCES Recipes(id) ON DELETE CASCADE
);

-- Tabla 4: Comentarios (Interacción social)
CREATE TABLE Comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES Recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Tabla 5: Lista de Compras (Preparada para sincronización offline)
CREATE TABLE ShoppingList (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ingredient_name VARCHAR(100) NOT NULL,
    quantity VARCHAR(50),
    is_checked BOOLEAN DEFAULT FALSE, -- Para el checkbox (comprado o no)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Clave para sincronizar el modo offline
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import mysql.connector
import re
import json
import bcrypt
import os
from uuid import uuid4
import urllib.parse 

from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN IA GEMINI ---
API_KEY = os.environ.get('GEMINI_API_KEY') 
client = genai.Client(api_key=API_KEY)

# --- CONFIGURACIÓN PARA FOTOS ---
CARPETA_PERFILES = "uploads/perfiles"
os.makedirs(CARPETA_PERFILES, exist_ok=True)

CARPETA_RESENAS = "uploads/resenas"
os.makedirs(CARPETA_RESENAS, exist_ok=True)

# Montamos la carpeta global static
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# --- MODELOS ---
class PeticionChef(BaseModel):
    ingredientes: str

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    password: str

class UsuarioLogin(BaseModel):
    email: str
    password: str

# 🔥 NUEVO MODELO: Para restablecer la contraseña
class RestablecerPassword(BaseModel):
    email: str
    nombre: str
    nueva_password: str

# Modelo para recibir los datos de actualización desde la app
class UsuarioActualizar(BaseModel):
    nombre: str = None
    usuario: str = None
    email: str = None

class Resena(BaseModel):
    receta_id: int
    usuario_id: int 
    estrellas: int
    comentario: str
    image_url: str = None 
    username: str = None 

def obtener_conexion():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'), 
        database=os.environ.get('DB_NAME', 'cook_and_share'), 
        user=os.environ.get('DB_USER', 'root'), 
        password=os.environ.get('DB_PASSWORD', ''),
        port=int(os.environ.get('DB_PORT', 3306))
    )

# --- RUTAS DE USUARIO & AUTENTICACIÓN ---
@app.post("/registro")
def registrar(u: UsuarioRegistro):
    try:
        conn = obtener_conexion(); cursor = conn.cursor()
        hash_pw = bcrypt.hashpw(u.password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (u.nombre, u.email, hash_pw.decode('utf-8')))
        conn.commit(); return {"mensaje": "ok"}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))
    finally: 
        if 'conn' in locals() and conn.is_connected(): conn.close()

@app.post("/login")
def login(u: UsuarioLogin):
    try:
        conn = obtener_conexion(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (u.email,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(u.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Devuelve el nombre real/apodo que está guardado en la base de datos
            return {"id": user['id'], "usuario": user['username'], "email": user['email']}
        raise HTTPException(status_code=401)
    finally: 
        if 'conn' in locals() and conn.is_connected(): conn.close()

# 🔥 NUEVA RUTA: Restablecer Contraseña (Validación sin correo)
@app.post("/restablecer-password")
def restablecer_password(r: RestablecerPassword):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        # Buscamos al usuario por su email y su nombre/apodo registrado
        cursor.execute("SELECT id FROM users WHERE email = %s AND username = %s", (r.email.lower(), r.nombre))
        usuario = cursor.fetchone()
        
        if usuario:
            # Si coinciden, encriptamos la nueva contraseña y la guardamos
            hash_pw = bcrypt.hashpw(r.nueva_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hash_pw.decode('utf-8'), usuario['id']))
            conn.commit()
            return {"mensaje": "ok"}
        else:
            raise HTTPException(status_code=404, detail="El correo o el nombre no coinciden con nuestros registros.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

# Ruta para editar los datos y guardar el apodo
@app.put("/usuario/actualizar/{user_id}")
def actualizar_usuario(user_id: int, u: UsuarioActualizar):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # El backend acepta 'nombre' o 'usuario' indistintamente
        nombre_final = u.nombre if u.nombre else u.usuario
        
        if not nombre_final or not u.email:
            raise HTTPException(status_code=400, detail="Faltan datos (nombre o email)")

        cursor.execute(
            "UPDATE users SET username = %s, email = %s WHERE id = %s", 
            (nombre_final, u.email, user_id)
        )
        conn.commit()
        return {"mensaje": "ok"}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))
    finally: 
        if 'conn' in locals() and conn.is_connected(): conn.close()

# --- RUTA PARA SUBIR FOTO DE PERFIL ---
@app.post("/usuario/{user_id}/subir-foto")
def subir_foto_perfil(user_id: int, file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1]
        nombre_archivo = f"{user_id}_{uuid4()}{ext}"
        ruta_completa = os.path.join(CARPETA_PERFILES, nombre_archivo)

        with open(ruta_completa, "wb") as buffer:
            buffer.write(file.file.read())

        base_url = os.environ.get('API_URL', 'https://app-movil-recetas.onrender.com')
        url_foto_publica = f"{base_url}/static/perfiles/{nombre_archivo}"
        return {"mensaje": "ok", "url_foto": url_foto_publica}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- RUTA PARA SUBIR FOTO DE RESEÑA ---
@app.post("/receta/{receta_id}/usuario/{user_id}/subir-foto-resena")
def subir_foto_resena(receta_id: int, user_id: int, file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")

        ext = os.path.splitext(file.filename)[1]
        nombre_archivo = f"r{receta_id}_u{user_id}_{uuid4()}{ext}"
        ruta_completa = os.path.join(CARPETA_RESENAS, nombre_archivo)

        with open(ruta_completa, "wb") as buffer:
            buffer.write(file.file.read())

        base_url = os.environ.get('API_URL', 'https://app-movil-recetas.onrender.com')
        url_foto_publica = f"{base_url}/static/resenas/{nombre_archivo}"
        return {"mensaje": "ok", "url_foto": url_foto_publica}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- RUTAS DE RECETAS ---
@app.get("/recetas/populares")
def recetas_populares():
    try:
        conn = obtener_conexion(); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM recipes ORDER BY id DESC")
        datos_db = cursor.fetchall()
        recetas_limpias = []
        for r in datos_db:
            texto = r['instructions'] if r['instructions'] else ""
            match_tiempo = re.search(r'Tiempo:\s*(\d+\s*\w+)', texto, re.IGNORECASE)
            tiempo_val = match_tiempo.group(1).strip() if match_tiempo else "20 min"
            texto_sin_tiempo = re.sub(r'Tiempo:.*', '', texto, flags=re.IGNORECASE).strip()
            partes = re.split(r'Preparación:|Instrucciones:', texto_sin_tiempo, flags=re.IGNORECASE)
            bloque_ing = partes[0].replace('Ingredientes:', '').strip()
            bloque_pasos = partes[1].strip() if len(partes) > 1 else ""
            lista_ing = [i.strip('- •*').strip() for i in re.split(r',|\n', bloque_ing) if len(i.strip()) > 2]
            if re.search(r'\d+\.', bloque_pasos):
                lista_pasos = [p.strip(' .•-*') for p in re.split(r'\d+\.|\d+\)', bloque_pasos) if p.strip()]
            else:
                lista_pasos = [p.strip() for p in bloque_pasos.split('.') if len(p.strip()) > 5]
            recetas_limpias.append({
                "id": r['id'], 
                "titulo": r['title'], 
                "tiempo": tiempo_val, 
                "dificultad": "Media",
                "categoria": r.get('category', 'General'),
                "creador": r.get('creator', 'Comunidad'),
                "imagen": r['image_url'] if r['image_url'] else "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
                "ingredientes": lista_ing if lista_ing else ["Ver preparación"],
                "instrucciones": lista_pasos if lista_pasos else [bloque_ing]
            })
        return recetas_limpias
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

# --- RUTA CHEF IA ---
@app.post("/chef-ia")
def chef_ia(p: PeticionChef):
    prompt = (
        f"Eres un chef experto. Crea una receta creativa con: {p.ingredientes}. "
        "Clasifícala en UNA de estas categorías exactas: 'Desayunos', 'Almuerzos', 'Cenas', 'Saludable', 'Postres', o 'Rápida'. "
        "Devuelve ESTRICTAMENTE un JSON válido con este formato: "
        "{\"titulo\": \"\", \"tiempo\": \"\", \"dificultad\": \"\", \"categoria\": \"\", \"ingredientes\": [], \"instrucciones\": []}"
    )
    try:
        res = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        json_txt = res.text.replace("```json", "").replace("```", "").strip()
        receta_gen = json.loads(json_txt)
        
        titulo_slug = receta_gen.get("titulo", "comida").replace(" ", "%20")
        link_img = f"https://image.pollinations.ai/prompt/fotografia%20gastronomica%20de%20{titulo_slug},%20alta%20resolucion?width=800&height=600&nologo=true"
        receta_gen["imagen"] = link_img

        texto_ing = "\n".join([f"- {i}" for i in receta_gen["ingredientes"]])
        texto_pasos = "\n".join([f"{idx+1}. {paso}" for idx, paso in enumerate(receta_gen["instrucciones"])])
        instrucciones_db = f"Tiempo: {receta_gen.get('tiempo', '20 min')}\nIngredientes:\n{texto_ing}\nPreparación:\n{texto_pasos}"
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipes (title, instructions, image_url, category, creator, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (receta_gen["titulo"], instrucciones_db, link_img, receta_gen.get("categoria", "General"), "Chef IA", 1)
        )
        conn.commit()
        receta_gen["id"] = cursor.lastrowid
        conn.close()

        return receta_gen
    except Exception as e:
        error_real = str(e)
        print(f"\n🚨 ERROR IA DETECTADO: {error_real}\n")
        return {
            "titulo": "🚨 Error del Chef IA", 
            "tiempo": "0 min", 
            "dificultad": "Error", 
            "categoria": "Error",
            "imagen": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800", 
            "ingredientes": [p.ingredientes], 
            "instrucciones": [
                "Ocurrió un error técnico con Gemini o tu Base de Datos:", 
                error_real, 
                "Revisa la terminal de Python."
            ]
        }

# --- RUTAS DE RESEÑAS ---
@app.post("/enviar-resena")
def resena(r: Resena):
    try:
        conn = obtener_conexion(); cursor = conn.cursor()
        query = "INSERT INTO resenas (receta_id, usuario_id, estrellas, comentario, image_url) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (r.receta_id, r.usuario_id, r.estrellas, r.comentario, r.image_url))
        conn.commit(); return {"status": "success"}
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))
    finally: 
        if 'conn' in locals() and conn.is_connected(): conn.close()

@app.get("/receta/{receta_id}/resenas")
def obtener_resenas(receta_id: int):
    try:
        conn = obtener_conexion(); cursor = conn.cursor(dictionary=True)
        query = """
            SELECT r.*, u.username 
            FROM resenas r 
            JOIN users u ON r.usuario_id = u.id 
            WHERE r.receta_id = %s 
            ORDER BY r.id DESC
        """
        cursor.execute(query, (receta_id,))
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e: return {"error": str(e)}

@app.get("/usuario/estadisticas/{user_id}")
def obtener_estadisticas_usuario(user_id: int):
    try:
        conn = obtener_conexion(); cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE user_id = %s", (user_id,))
        creadas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM resenas WHERE usuario_id = %s", (user_id,))
        hechas = cursor.fetchone()[0]
        conn.close()
        return {"creadas": creadas, "hechas": hechas}
    except Exception as e:
        print(f"Error stats: {e}")
        return {"creadas": 0, "hechas": 0}

# --- CREACIÓN DE RECETAS MANUALES ---
class RecetaManual(BaseModel):
    titulo: str
    tiempo: str
    categoria: str
    ingredientes: str
    instrucciones: str
    creador: str
    user_id: int

@app.post("/recetas/nueva")
def crear_receta_manual(r: RecetaManual):
    try:
        titulo_slug = r.titulo.replace(" ", "%20")
        link_img = f"https://image.pollinations.ai/prompt/fotografia%20gastronomica%20de%20{titulo_slug},%20alta%20resolucion?width=800&height=600&nologo=true"

        lista_ing = [i.strip() for i in r.ingredientes.split('\n') if i.strip()]
        lista_pasos = [p.strip() for p in r.instrucciones.split('\n') if p.strip()]

        texto_ing = "\n".join([f"- {i}" for i in lista_ing])
        texto_pasos = "\n".join([f"{idx+1}. {paso}" for idx, paso in enumerate(lista_pasos)])
        
        instrucciones_db = f"Tiempo: {r.tiempo}\nIngredientes:\n{texto_ing}\nPreparación:\n{texto_pasos}"

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipes (title, instructions, image_url, category, creator, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (r.titulo, instrucciones_db, link_img, r.categoria, r.creador, r.user_id)
        )
        conn.commit()
        receta_id = cursor.lastrowid
        conn.close()

        return {"mensaje": "ok", "id": receta_id}
    except Exception as e:
        print(f"Error creando receta manual: {e}")
        raise HTTPException(status_code=400, detail=str(e))

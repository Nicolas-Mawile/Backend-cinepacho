# ⚡ QUICK START - Ejecución en 5 minutos

## 🎯 Objetivo: Ejecutar el servidor y acceder a la API

---

## 📋 Pre-requisitos
- ✅ Python 3.10+ instalado
- ✅ Estás en: `c:\Users\ARNOLD\Desktop\Arlo\U\Diseño de Software\Proyecto\Code\cinepachobackend`

---

## ⏱️ TIMER: 5 MINUTOS

### ⏲️ **MIN 0-1: Crear y Activar Entorno Virtual**

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

✅ Deberías ver `(venv)` en tu terminal

---

### ⏲️ **MIN 1-3: Instalar Dependencias**

```powershell
pip install -r requirements.txt
```

Espera a que termine (instalará ~20 paquetes)

---

### ⏲️ **MIN 3-4: Ejecutar Servidor**

```powershell
python run.py
```

Deberías ver:
```
🚀 Inicializando Cinepacho Backend...
✅ Base de datos inicializada
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### ⏲️ **MIN 4-5: Verificar en Navegador**

Abre en tu navegador **3 pestañas:**

#### 🟢 **Pestaña 1: Health Check**
```
http://localhost:8000/health
```
Verás:
```json
{"status": "ok", "app": "Cinepacho Backend"}
```

#### 📚 **Pestaña 2: Swagger Docs**
```
http://localhost:8000/docs
```
Verás interfaz interactiva para probar endpoints

#### 📖 **Pestaña 3: ReDoc**
```
http://localhost:8000/redoc
```
Verás documentación limpia de la API

---

## ✅ ¡ÉXITO!

Si ves las 3 páginas sin errores, tu servidor está corriendo perfectamente.

---

## 🔍 ¿Qué Sucedió?

1. **Entorno Virtual:** Aislaste Python del sistema
2. **Dependencias:** Instalaste FastAPI, SQLAlchemy, etc.
3. **BD:** Se creó automáticamente `cinepacho.db`
4. **Servidor:** FastAPI + Uvicorn corriendo en puerto 8000

---

## 📝 Próximos Pasos

### Opción A: Probar un Endpoint
En la pestaña `/docs`, haz clic en:
```
GET /health
```
Luego "Try it out"

### Opción B: Salir (y reanudar después)

```powershell
Ctrl+C  # Detiene el servidor
deactivate  # Desactiva entorno virtual
```

Para volver a iniciar:
```powershell
.\venv\Scripts\Activate.ps1
python run.py
```

### Opción C: Más Información

Lee estos archivos:
- `SETUP.md` - Instalación detallada
- `TODO.md` - Qué falta implementar
- `ANALYSIS.md` - Análisis completo del proyecto
- `README.md` - Documentación general

---

## 🆘 Si algo falla...

### Error: "ModuleNotFoundError"
```powershell
# Verifica que el venv esté activado
# Deberías ver (venv) al inicio de la línea
python -c "import fastapi"  # Prueba
```

### Error: "Port already in use"
```powershell
# El puerto 8000 está ocupado
# Intenta otro puerto:
uvicorn app.main:app --port 8001 --reload
```

### Error: "Permission denied" en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📊 Checklist

- [ ] ✅ venv creado
- [ ] ✅ venv activado (ves `(venv)`)
- [ ] ✅ dependencias instaladas (`pip list` muestra FastAPI)
- [ ] ✅ servidor corriendo (`python run.py`)
- [ ] ✅ health check funciona (`http://localhost:8000/health`)
- [ ] ✅ Swagger accesible (`http://localhost:8000/docs`)

Si todas están ✅, **¡FELICITACIONES!** 🎉

Tu servidor Cinepacho Backend está 100% funcional.

---

**¿Listos? ¡A programar! 🚀**

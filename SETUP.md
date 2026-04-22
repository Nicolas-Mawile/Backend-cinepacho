# 🔧 Guía de Instalación - Cinepacho Backend

## ✅ Checklist Pre-Instalación

- [ ] Python 3.10 o superior instalado
- [ ] pip actualizado
- [ ] Git instalado
- [ ] Terminal accesible

## 📝 Pasos de Instalación

### **PASO 1: Preparar el entorno**

```bash
# Navegar al directorio del proyecto
cd c:\Users\ARNOLD\Desktop\Arlo\U\Diseño de Software\Proyecto\Code\cinepachobackend
```

### **PASO 2: Crear entorno virtual**

```bash
# Windows
python -m venv venv

# Esto crea la carpeta 'venv' con Python aislado
```

### **PASO 3: Activar entorno virtual**

```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# Si obtienes error de permisos:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Luego intenta de nuevo

# CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

✅ Deberías ver `(venv)` al inicio de tu terminal

### **PASO 4: Instalar dependencias**

```bash
pip install -r requirements.txt

# Para desarrollo (con tools de linting, testing):
pip install -r requirements-dev.txt
```

### **PASO 5: Verificar instalación**

```bash
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} ✅')"
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__} ✅')"
```

### **PASO 6: Ejecutar la aplicación**

```bash
python run.py
```

Deberías ver:
```
🚀 Inicializando Cinepacho Backend...
✅ Base de datos inicializada
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **PASO 7: Verificar que funciona**

Abre en tu navegador:
```
http://localhost:8000/health
```

Deberías ver:
```json
{"status": "ok", "app": "Cinepacho Backend"}
```

## 🎯 Endpoints de Prueba

### Health Check
```bash
curl http://localhost:8000/health
```

### Documentación API
```
http://localhost:8000/docs
```

## ❌ Solución de Problemas

### **Problema: "ModuleNotFoundError: No module named 'app'"**

**Solución:**
```bash
# Verifica que el venv esté activado
python -c "import sys; print(sys.executable)"
# Debería mostrar una ruta dentro de 'venv'

# Si no, activa de nuevo:
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate
```

### **Problema: "Permission denied" en Activate.ps1**

**Solución (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### **Problema: Port 8000 already in use**

**Solución:**
```bash
# Cambiar puerto en run.py o ejecutar:
uvicorn app.main:app --port 8001 --reload
```

### **Problema: "ModuleNotFoundError: No module named 'pydantic_settings'"**

**Solución:**
```bash
pip install --upgrade pydantic-settings
```

## 🔄 Comandos Útiles

```bash
# Ver versiones instaladas
pip list

# Actualizar pip
python -m pip install --upgrade pip

# Desactivar venv
deactivate

# Reinstalar todas las dependencias
pip install --force-reinstall -r requirements.txt

# Ver estructura del proyecto
tree /F  # Windows
tree     # Linux/Mac
```

## 🚀 Próximos Pasos

1. ✅ Instalar dependencias
2. ✅ Ejecutar servidor
3. 🔜 Acceder a `http://localhost:8000/docs`
4. 🔜 Implementar endpoints (actualmente son stubs)
5. 🔜 Conectar BD a endpoints
6. 🔜 Implementar autenticación
7. 🔜 Escribir tests

## 📞 Ayuda

Si tienes problemas:

1. Verifica el archivo `.env` existe
2. Confirma que el venv está activado: `(venv)` visible en terminal
3. Intenta: `pip install --upgrade pip setuptools wheel`
4. Revisa los logs en la terminal

---

**¡Listo para comenzar! 🎉**

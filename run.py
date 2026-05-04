#!/usr/bin/env python
"""
Script para ejecutar la aplicación Cinepacho Backend.

Uso:
    python run.py                  # Ejecuta en http://localhost:8000
    python run.py --host 0.0.0.0   # Accesible desde la red
    python run.py --port 9000      # En puerto 9000
"""

import uvicorn
import sys

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )

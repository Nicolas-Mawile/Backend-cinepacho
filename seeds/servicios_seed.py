# app/infrastructure/seeds/servicio_seed.py
from sqlalchemy import select
from app.database import SessionLocal
from app.infrastructure.models.servicio import Servicio

SERVICIOS = [
    "Atención al cliente",
    "Servicio de cafetería",
    "Comodidad de la sala",
    "Limpieza de la sala",
    "Calidad de proyección",
    "Calidad de sonido",
]


def run():
    db = SessionLocal()
    try:
        for nombre_servicio in SERVICIOS:
            servicio_existente = db.execute(select(Servicio).where(Servicio.nombre == nombre_servicio)).scalar_one_or_none()

            if not servicio_existente:
                nuevo_servicio = Servicio(nombre=nombre_servicio)

                db.add(nuevo_servicio)
                print(f"✅ Servicio creado: {nombre_servicio}")

            else:
                print(f"⚠️ Servicio ya existe: {nombre_servicio}")

        db.commit()
        print("🎉 Seed de servicios completado")

    finally:
        db.close()

if __name__ == "__main__":
    run()
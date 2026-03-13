#!/usr/bin/env python3
"""
Seeder para crear usuarios y empresas iniciales.
Crea un usuario con cédula=12345678 (contraseña por defecto: password123).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Añadir el directorio raíz del backend (donde está main.py) al path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import select

from app.config import settings
from app.infrastructure.database.models import EnterpriseModel, UserModel
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.security.password import BcryptPasswordHasher

# Usuario por defecto del seeder
SEED_CEDULA = "12345678"
SEED_PASSWORD = "password123"
SEED_FIRST_NAME = "Usuario"
SEED_LAST_NAME = "Seeder"
SEED_ENTERPRISE_NAME = "Empresa Demo"
SEED_NIT = "900123456"


def run_seed() -> None:
    hasher = BcryptPasswordHasher()
    db = SessionLocal()

    try:
        # Crear o obtener empresa
        enterprise = db.execute(
            select(EnterpriseModel).where(EnterpriseModel.nit == SEED_NIT)
        ).scalar_one_or_none()

        if not enterprise:
            enterprise = EnterpriseModel(
                name=SEED_ENTERPRISE_NAME,
                nit=SEED_NIT,
            )
            db.add(enterprise)
            db.commit()
            db.refresh(enterprise)
            print(f"  Empresa creada: {enterprise.name} (NIT: {enterprise.nit})")
        else:
            print(f"  Empresa existente: {enterprise.name} (NIT: {enterprise.nit})")

        # Crear usuario si no existe
        existing = db.execute(
            select(UserModel).where(UserModel.cedula == SEED_CEDULA)
        ).scalar_one_or_none()

        if existing:
            print(f"  Usuario ya existe: cédula={SEED_CEDULA}")
            return

        user = UserModel(
            first_name=SEED_FIRST_NAME,
            last_name=SEED_LAST_NAME,
            cedula=SEED_CEDULA,
            hashed_password=hasher.hash(SEED_PASSWORD),
            enterprise_id=enterprise.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"  Usuario creado: cédula={SEED_CEDULA}, contraseña={SEED_PASSWORD}")

    finally:
        db.close()


if __name__ == "__main__":
    print("Ejecutando seeder...")
    run_seed()
    print("Listo.")

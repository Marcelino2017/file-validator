#!/bin/bash
set -e

# Esperar a que MySQL esté listo (cuando corre en Docker)
if [ -n "$DATABASE_URL" ]; then
  echo "Esperando a la base de datos..."
  sleep 5
fi

echo "Ejecutando migraciones..."
alembic upgrade head

echo "Iniciando servidor..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

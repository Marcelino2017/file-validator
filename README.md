# mi-proyecto-senior

Sistema Full Stack con FastAPI + React, diseñado con Arquitectura Hexagonal (Ports & Adapters), principios SOLID y Clean Architecture en frontend.

## Estructura

```text
mi-proyecto-senior/
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── interfaces/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── hooks/
    │   ├── pages/
    │   └── context/
    └── package.json
```

## Backend

- `domain`: entidades puras (`User`, `Enterprise`, `Profile`, `PDFDocument`) e interfaces abstractas de puertos.
- `application`: casos de uso (`RegisterUser`, `LoginUser`, `ValidateAndUploadPDF`).
- `infrastructure`: adaptadores concretos (SQLAlchemy/MySQL, JWT, hash de password, almacenamiento local, factoría de validadores).
- `interfaces`: entrada HTTP (FastAPI), esquemas Pydantic, dependencias y rutas.

Validaciones:
- Cédula: `^[0-9]{6,12}$`
- NIT: `^[0-9]{9,15}(-[0-9])?$`
- PDF: validación de extensión, MIME (`application/pdf`), cabecera binaria (`%PDF`) y presencia de la cédula del usuario en el contenido del documento (incluye OCR para PDFs escaneados como imagen).
- La cédula se detecta en variantes como `1083005305`, `1.083.005.305`, `CC1083005305` o `CC 1.083.005.305`.

Requisito OCR para PDFs escaneados:
- Instalar Tesseract OCR en el sistema operativo y asegurarse de que el binario `tesseract` esté disponible en `PATH`.

### Ejecutar backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Variables clave en `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/proyecto_senior?charset=utf8mb4
```

## Frontend

- `api`: cliente Axios y servicios por módulo.
- `hooks`: formularios y lógica de subida de archivos.
- `components`: UI atómica (Button, Input, Card, Layout).
- `context`: sesión global con `AuthContext`.
- `pages`: Login, Register y Dashboard.

### Ejecutar frontend

```bash
cd frontend
npm install
npm run dev
```

## Flujo principal

1. Registro de usuario con nombre, apellido, cédula, empresa, NIT y contraseña.
2. Login por cédula + contraseña para obtener JWT.
3. Subida de PDF autenticada con validación MIME + firma binaria.

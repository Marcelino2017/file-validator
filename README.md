# Proyecto Senior - Sistema de Validacion de Documentos PDF

Sistema Full Stack con **FastAPI + React** para la gestion de usuarios corporativos y validacion inteligente de documentos PDF. Diseñado con **Arquitectura Hexagonal** (Ports & Adapters), principios **SOLID** y **Clean Architecture**.

El sistema verifica que los PDFs subidos contengan la cedula del usuario autenticado, soportando tanto PDFs digitales como documentos escaneados (imagenes) mediante un pipeline de extraccion de texto de 5 capas con OCR.

---

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Clonar y Configurar el Proyecto](#clonar-y-configurar-el-proyecto)
3. [Ejecutar el Proyecto](#ejecutar-el-proyecto)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Arquitectura del Backend](#arquitectura-del-backend)
6. [Pipeline de Validacion de PDF (5 Capas)](#pipeline-de-validacion-de-pdf-5-capas)
7. [Endpoints de la API](#endpoints-de-la-api)
8. [Arquitectura del Frontend](#arquitectura-del-frontend)
9. [Funciones y Clases Creadas](#funciones-y-clases-creadas)
10. [Flujo Principal de la Aplicacion](#flujo-principal-de-la-aplicacion)

---

## Requisitos Previos

Antes de clonar el proyecto, asegurate de tener instalado:

| Herramienta | Version minima | Proposito |
|-------------|---------------|-----------|
| **Python** | 3.10+ | Backend (FastAPI) |
| **Node.js** | 18+ | Frontend (React + Vite) |
| **MySQL** | 8.0+ | Base de datos relacional |
| **Tesseract OCR** | 5.0+ | Reconocimiento optico de caracteres para PDFs escaneados |

### Instalar Tesseract OCR (Windows)

1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar el instalador (ruta por defecto: `C:\Program Files\Tesseract-OCR\`)
3. Durante la instalacion, marcar el paquete de idioma **Spanish** (`spa`) ademas de English
4. Verificar la instalacion:

```bash
tesseract --version
```

### Crear la base de datos MySQL

```sql
CREATE DATABASE proyecto_senior CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Clonar y Configurar el Proyecto

### Paso 1: Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd proyectSenior
```

### Paso 2: Configurar el Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activar entorno virtual (Windows CMD)
.venv\Scripts\activate.bat

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecuta el servidor:
uvicorn main:app --reload
```

### Paso 3: Configurar variables de entorno del Backend

Copiar el archivo de ejemplo y editarlo:

```bash
copy .env.example .env
```

Contenido de `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/proyecto_senior?charset=utf8mb4
JWT_SECRET_KEY=change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
UPLOAD_DIR=uploaded_files
CORS_ORIGINS=http://localhost:5173
```

| Variable | Descripcion |
|----------|-------------|
| `DATABASE_URL` | Cadena de conexion a MySQL (usuario, contraseña, host, puerto, nombre de BD) |
| `JWT_SECRET_KEY` | Clave secreta para firmar tokens JWT (cambiar en produccion) |
| `JWT_ALGORITHM` | Algoritmo de cifrado del JWT (HS256 por defecto) |
| `JWT_EXPIRE_MINUTES` | Tiempo de expiracion del token en minutos |
| `UPLOAD_DIR` | Directorio donde se almacenan los PDFs subidos |
| `CORS_ORIGINS` | Origenes permitidos para peticiones CORS (URL del frontend) |

### Paso 4: Configurar el Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install
```

Copiar el archivo de ejemplo y editarlo:

```bash
copy .env.example .env
```

Contenido de `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Ejecutar el Proyecto

### Terminal 1 - Backend

```bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

El servidor arranca en `http://localhost:8000`. La documentacion interactiva de la API esta disponible en `http://localhost:8000/docs`.

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

La aplicacion web arranca en `http://localhost:5173`.

---

## Estructura del Proyecto

```text
proyectSenior/
├── README.md
├── backend/
│   ├── .env                          # Variables de entorno (no versionado)
│   ├── .env.example                  # Plantilla de variables de entorno
│   ├── main.py                       # Punto de entrada: crea la app FastAPI
│   ├── requirements.txt              # Dependencias de Python
│   └── app/
│       ├── config.py                 # Configuracion con Pydantic Settings
│       ├── domain/                   # === CAPA DE DOMINIO ===
│       │   ├── entities.py           # Entidades: Enterprise, User, Profile, PDFDocument
│       │   └── interfaces.py         # Puertos abstractos (ABC): repos, storage, auth
│       ├── application/              # === CAPA DE APLICACION ===
│       │   ├── exceptions.py         # Excepciones de negocio
│       │   ├── auth_service.py       # Casos de uso: RegisterUser, LoginUser
│       │   └── pdf_service.py        # Caso de uso: ValidateAndUploadPDF (5 capas OCR)
│       ├── infrastructure/           # === CAPA DE INFRAESTRUCTURA ===
│       │   ├── database/
│       │   │   ├── base.py           # Base declarativa de SQLAlchemy
│       │   │   ├── session.py        # Motor y sesion de base de datos
│       │   │   ├── models.py         # Modelos ORM: EnterpriseModel, UserModel, PDFDocumentModel
│       │   │   └── repositories.py   # Implementaciones concretas de los repositorios
│       │   ├── security/
│       │   │   ├── jwt_provider.py   # Proveedor JWT con python-jose
│       │   │   └── password.py       # Hash de contraseñas con pbkdf2_sha256
│       │   └── storage/
│       │       ├── local_storage.py  # Almacenamiento local en disco
│       │       └── validators.py     # Validadores de archivos (MIME, extension, firma binaria)
│       └── interfaces/               # === CAPA DE INTERFACES ===
│           ├── dependencies.py       # Inyeccion de dependencias de FastAPI
│           ├── schemas/
│           │   ├── auth.py           # Esquemas Pydantic de autenticacion
│           │   └── pdf.py            # Esquema de respuesta para subida de PDF
│           └── api_v1/
│               ├── router.py         # Router agregador de rutas
│               ├── auth_routes.py    # Rutas: /auth/register, /auth/login, /auth/me
│               └── pdf_routes.py     # Ruta: /documents/upload-pdf
│
└── frontend/
    ├── .env                          # Variables de entorno del frontend
    ├── .env.example                  # Plantilla
    ├── index.html                    # HTML raiz
    ├── package.json                  # Dependencias de Node.js
    ├── vite.config.js                # Configuracion de Vite
    ├── tailwind.config.js            # Configuracion de Tailwind CSS
    ├── postcss.config.js             # Configuracion de PostCSS
    └── src/
        ├── main.jsx                  # Punto de entrada: React + BrowserRouter + AuthProvider
        ├── App.jsx                   # Definicion de rutas protegidas
        ├── index.css                 # Estilos globales + Tailwind
        ├── api/
        │   ├── axiosClient.js        # Cliente Axios con interceptor de token Bearer
        │   ├── authService.js        # Servicios: registerUser, loginUser, fetchProfile
        │   └── pdfService.js         # Servicio: uploadPdf
        ├── context/
        │   └── AuthContext.jsx       # Contexto global de autenticacion
        ├── hooks/
        │   ├── useAuthForm.js        # Hooks de formularios con react-hook-form
        │   └── useUpload.js          # Hook de subida de PDF con validacion MIME
        ├── pages/
        │   ├── LoginPage.jsx         # Pagina de inicio de sesion
        │   ├── RegisterPage.jsx      # Pagina de registro corporativo
        │   └── DashboardPage.jsx     # Panel principal con subida de PDF
        └── components/
            ├── Button.jsx            # Componente de boton reutilizable
            ├── Card.jsx              # Componente de tarjeta con titulo y subtitulo
            ├── Input.jsx             # Componente de input con label y error
            └── Layout.jsx            # Layout centrado de pagina completa
```

---

## Arquitectura del Backend

El backend sigue la **Arquitectura Hexagonal** (Ports & Adapters) con 4 capas bien definidas:

```text
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACES (FastAPI)                      │
│  api_v1/auth_routes.py  │  api_v1/pdf_routes.py            │
│  schemas/auth.py        │  schemas/pdf.py                   │
│  dependencies.py (Inyeccion de Dependencias)                │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION (Casos de Uso)                │
│  auth_service.py → RegisterUser, LoginUser                  │
│  pdf_service.py  → ValidateAndUploadPDF (5 capas OCR)      │
│  exceptions.py   → Excepciones de negocio                   │
├─────────────────────────────────────────────────────────────┤
│                    DOMAIN (Entidades + Puertos)              │
│  entities.py   → User, Enterprise, PDFDocument, Profile     │
│  interfaces.py → UserRepository, EnterpriseRepository,      │
│                  PDFRepository, FileStorage, FileValidator,  │
│                  PasswordHasher, TokenProvider               │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE (Adaptadores)              │
│  database/   → SQLAlchemy (MySQL), modelos ORM, repos       │
│  security/   → JWT (python-jose), Password (pbkdf2_sha256)  │
│  storage/    → Disco local, validadores de PDF              │
└─────────────────────────────────────────────────────────────┘
```

### Principios aplicados

- **SOLID**: Cada clase tiene una sola responsabilidad. Las dependencias se inyectan por interfaces abstractas.
- **Dependency Inversion**: La capa de aplicacion depende de interfaces abstractas (`UserRepository`, `FileStorage`), no de implementaciones concretas (`SQLAlchemyUserRepository`, `LocalDiskStorage`).
- **Ports & Adapters**: Los puertos estan en `domain/interfaces.py` y los adaptadores en `infrastructure/`.

---

## Pipeline de Validacion de PDF (5 Capas)

El sistema valida que el PDF subido contenga la cedula del usuario autenticado usando un pipeline progresivo de 5 capas. Se detiene en cuanto encuentra la cedula en cualquier capa (optimizacion de rendimiento).

```text
PDF subido por el usuario
         │
         ▼
┌─── Capa 1: pypdf ──────────────────────────────────┐
│ Extraccion de texto nativo del PDF                   │
│ Funciona con: PDFs digitales simples                 │
│ Funcion: _extract_text_pypdf()                       │
└──────────────┬──────────────────────────────────────┘
         │ Si no encuentra la cedula...
         ▼
┌─── Capa 2: pdfplumber ─────────────────────────────┐
│ Extraccion con mejor manejo de layouts complejos     │
│ Funciona con: PDFs con tablas, columnas, fuentes     │
│ Funcion: _extract_text_pdfplumber()                  │
└──────────────┬──────────────────────────────────────┘
         │ Si no encuentra la cedula...
         ▼
┌─── Capa 3: PyMuPDF (fitz) ─────────────────────────┐
│ Extraccion de texto nativo alternativa               │
│ Funciona con: PDFs que los anteriores no logran leer │
│ Funcion: _extract_text_fitz()                        │
└──────────────┬──────────────────────────────────────┘
         │ Si no encuentra la cedula...
         ▼
┌─── Capa 4: OCR de imagenes incrustadas ────────────┐
│ Extrae cada imagen embebida del PDF individualmente  │
│ y le aplica OCR con Tesseract                        │
│ Funciona con: Fotos/escaneos pegados dentro de un    │
│ documento (ej: Word con imagen exportado a PDF)      │
│ Funcion: _extract_text_from_embedded_images()        │
└──────────────┬──────────────────────────────────────┘
         │ Si no encuentra la cedula...
         ▼
┌─── Capa 5: OCR de pagina completa ─────────────────┐
│ Renderiza cada pagina como imagen a multiples zooms  │
│ (2x, 3x, 4x) y con recortes (completa, mitad       │
│ superior, mitad inferior)                            │
│ Funciona con: PDFs 100% escaneados (imagen completa) │
│ Funcion: _extract_text_ocr()                         │
└─────────────────────────────────────────────────────┘
```

### Preprocesamiento de imagen para OCR

Cada imagen pasa por 5 versiones de preprocesamiento para maximizar la precision del OCR:

| Version | Tecnica | Proposito |
|---------|---------|-----------|
| 1 | Escala de grises (sin procesar) | Imagen original en gris |
| 2 | GaussianBlur (3x3) | Reduccion de ruido |
| 3 | Otsu Threshold | Binarizacion automatica por histograma |
| 4 | Adaptive Threshold Gaussian | Binarizacion adaptativa por region |
| 5 | Bilateral Filter + Otsu | Suavizado preservando bordes + binarizacion |

### Deteccion flexible de cedula

El sistema busca la cedula en multiples formatos:

| Formato | Ejemplo | Fuente tipica |
|---------|---------|---------------|
| Digitos puros | `1083005305` | Texto digital |
| Con puntos | `1.083.005.305` | Documentos formales |
| Con guiones | `1-083-005-305` | Formularios |
| Con prefijo CC | `C.C. No. 1.083.005.305` | Certificados |
| Con espacios | `1 083 005 305` | OCR con separadores |

Ademas, para texto extraido por OCR se aplica normalizacion de caracteres comunes que Tesseract confunde:

| Caracter OCR | Se interpreta como |
|-------------|-------------------|
| O, o, Q, D | 0 |
| I, l, L, \| | 1 |
| Z, z | 2 |
| S, s, $ | 5 |
| G | 6 |
| B | 8 |
| g | 9 |

---

## Endpoints de la API

Base URL: `http://localhost:8000/api/v1`

### Autenticacion

| Metodo | Ruta | Descripcion | Autenticacion |
|--------|------|-------------|---------------|
| `POST` | `/auth/register` | Registro de usuario con empresa | No |
| `POST` | `/auth/login` | Login por cedula + contraseña → JWT | No |
| `GET` | `/auth/me` | Perfil del usuario autenticado | Si (Bearer Token) |

#### POST /auth/register

```json
{
  "first_name": "Marcelino",
  "last_name": "Mejia",
  "cedula": "1083005305",
  "enterprise_name": "CI. Tecnicas Baltime de Colombia",
  "nit": "900123456",
  "password": "micontraseña123"
}
```

Respuesta `201 Created`:

```json
{
  "id": 1,
  "first_name": "Marcelino",
  "last_name": "Mejia",
  "cedula": "1083005305",
  "enterprise_id": 1
}
```

#### POST /auth/login

```json
{
  "cedula": "1083005305",
  "password": "micontraseña123"
}
```

Respuesta `200 OK`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": 1,
  "cedula": "1083005305"
}
```

#### GET /auth/me

Header: `Authorization: Bearer <token>`

Respuesta `200 OK`:

```json
{
  "id": 1,
  "first_name": "Marcelino",
  "last_name": "Mejia",
  "cedula": "1083005305",
  "enterprise_id": 1
}
```

### Documentos

| Metodo | Ruta | Descripcion | Autenticacion |
|--------|------|-------------|---------------|
| `POST` | `/documents/upload-pdf` | Subida y validacion de PDF | Si (Bearer Token) |

#### POST /documents/upload-pdf

Content-Type: `multipart/form-data`
Header: `Authorization: Bearer <token>`
Campo: `file` (archivo PDF)

Validaciones realizadas:
1. Extension del archivo es `.pdf`
2. Tipo MIME es `application/pdf`
3. Cabecera binaria empieza con `%PDF`
4. El contenido del PDF contiene la cedula del usuario autenticado (5 capas de extraccion)

Respuesta `201 Created`:

```json
{
  "id": 1,
  "filename": "certificado_laboral.pdf",
  "mime_type": "application/pdf",
  "sha256": "a1b2c3d4e5f6...",
  "storage_path": "uploaded_files/abc123.pdf"
}
```

---

## Arquitectura del Frontend

```text
┌─────────────────────────────────────────────────────┐
│                    PAGINAS                            │
│  LoginPage → RegisterPage → DashboardPage            │
├─────────────────────────────────────────────────────┤
│              HOOKS / CONTEXTO                        │
│  useAuthForm  │  useUpload  │  AuthContext           │
├─────────────────────────────────────────────────────┤
│              COMPONENTES UI                          │
│  Button  │  Input  │  Card  │  Layout                │
├─────────────────────────────────────────────────────┤
│              CAPA DE API                             │
│  axiosClient (interceptor Bearer)                    │
│  authService  │  pdfService                          │
└─────────────────────────────────────────────────────┘
```

### Tecnologias del Frontend

| Libreria | Version | Proposito |
|----------|---------|-----------|
| React | 18.3 | Libreria de UI |
| React Router DOM | 7.2 | Navegacion SPA |
| React Hook Form | 7.54 | Manejo de formularios |
| Axios | 1.8 | Cliente HTTP |
| Tailwind CSS | 3.4 | Estilos utilitarios |
| Vite | 6.2 | Bundler y dev server |

---

## Funciones y Clases Creadas

### Capa de Dominio (`domain/`)

| Archivo | Clase/Funcion | Descripcion |
|---------|---------------|-------------|
| `entities.py` | `Enterprise` | Dataclass de empresa (name, nit) |
| `entities.py` | `User` | Dataclass de usuario (first_name, last_name, cedula, hashed_password, enterprise_id) |
| `entities.py` | `Profile` | Dataclass de perfil (user_id, enterprise_name, nit) |
| `entities.py` | `PDFDocument` | Dataclass de documento PDF (filename, mime_type, storage_path, sha256, user_id, enterprise_id) |
| `interfaces.py` | `EnterpriseRepository` | Puerto abstracto: get_by_nit(), create() |
| `interfaces.py` | `UserRepository` | Puerto abstracto: get_by_cedula(), get_by_id(), create() |
| `interfaces.py` | `PDFRepository` | Puerto abstracto: create() |
| `interfaces.py` | `PasswordHasher` | Puerto abstracto: hash(), verify() |
| `interfaces.py` | `TokenProvider` | Puerto abstracto: create_access_token(), get_subject() |
| `interfaces.py` | `FileStorage` | Puerto abstracto: save() → (path, sha256) |
| `interfaces.py` | `FileValidator` | Puerto abstracto: validate() |
| `interfaces.py` | `FileValidatorFactory` | Puerto abstracto: for_file() |

### Capa de Aplicacion (`application/`)

| Archivo | Clase/Funcion | Descripcion |
|---------|---------------|-------------|
| `exceptions.py` | `ApplicationError` | Excepcion base |
| `exceptions.py` | `ConflictError` | Conflicto (ej: cedula duplicada) |
| `exceptions.py` | `NotFoundError` | Recurso no encontrado |
| `exceptions.py` | `UnauthorizedError` | No autorizado |
| `exceptions.py` | `ValidationError` | Error de validacion |
| `auth_service.py` | `RegisterUserInput` | Dataclass de entrada para registro |
| `auth_service.py` | `LoginInput` | Dataclass de entrada para login |
| `auth_service.py` | `AuthResult` | Dataclass de resultado de autenticacion |
| `auth_service.py` | `RegisterUser` | Caso de uso: registra usuario + empresa |
| `auth_service.py` | `RegisterUser.execute()` | Valida cedula/NIT, verifica duplicados, crea empresa si no existe, hashea password, crea usuario |
| `auth_service.py` | `LoginUser` | Caso de uso: autentica por cedula + password |
| `auth_service.py` | `LoginUser.execute()` | Busca usuario por cedula, verifica password, genera JWT |
| `pdf_service.py` | `ValidateAndUploadPDFInput` | Dataclass de entrada para subida de PDF |
| `pdf_service.py` | `ValidateAndUploadPDF` | Caso de uso principal: valida y almacena PDF |
| `pdf_service.py` | `.execute()` | Busca usuario, valida archivo, verifica cedula en PDF, guarda en disco, crea registro en BD |
| `pdf_service.py` | `._pdf_contains_user_cedula()` | Orquesta las 5 capas de extraccion |
| `pdf_service.py` | `._contains_cedula_variant()` | Busca cedula por digitos normalizados y por patron regex |
| `pdf_service.py` | `._build_cedula_pattern()` | Construye regex que acepta separadores entre digitos |
| `pdf_service.py` | `._normalize_digits()` | Extrae solo digitos de un texto |
| `pdf_service.py` | `._normalize_ocr_text()` | Corrige caracteres que OCR confunde con digitos |
| `pdf_service.py` | `._extract_text_pypdf()` | **Capa 1**: extraccion con pypdf |
| `pdf_service.py` | `._extract_text_pdfplumber()` | **Capa 2**: extraccion con pdfplumber |
| `pdf_service.py` | `._extract_text_fitz()` | **Capa 3**: extraccion con PyMuPDF (fitz) |
| `pdf_service.py` | `._extract_text_from_embedded_images()` | **Capa 4**: OCR sobre imagenes individuales incrustadas en el PDF |
| `pdf_service.py` | `._extract_text_ocr()` | **Capa 5**: OCR sobre pagina completa renderizada |
| `pdf_service.py` | `._configure_tesseract()` | Configura ruta del ejecutable de Tesseract en Windows |
| `pdf_service.py` | `._preprocess_for_ocr()` | Genera 5 versiones preprocesadas de cada imagen |
| `pdf_service.py` | `._run_tesseract()` | Ejecuta Tesseract con 3 modos PSM y fallback de idioma |

### Capa de Infraestructura (`infrastructure/`)

| Archivo | Clase/Funcion | Descripcion |
|---------|---------------|-------------|
| `database/base.py` | `Base` | Base declarativa de SQLAlchemy |
| `database/session.py` | `engine` | Motor de conexion a MySQL |
| `database/session.py` | `SessionLocal` | Fabrica de sesiones |
| `database/session.py` | `get_db_session()` | Generador de sesiones para inyeccion de dependencias |
| `database/models.py` | `EnterpriseModel` | Modelo ORM de la tabla `enterprises` |
| `database/models.py` | `UserModel` | Modelo ORM de la tabla `users` (cedula unica, indexada) |
| `database/models.py` | `PDFDocumentModel` | Modelo ORM de la tabla `pdf_documents` |
| `database/repositories.py` | `SQLAlchemyEnterpriseRepository` | Implementacion concreta de EnterpriseRepository |
| `database/repositories.py` | `SQLAlchemyUserRepository` | Implementacion concreta de UserRepository |
| `database/repositories.py` | `SQLAlchemyPDFRepository` | Implementacion concreta de PDFRepository |
| `security/jwt_provider.py` | `JoseJWTTokenProvider` | Implementacion de TokenProvider con python-jose |
| `security/password.py` | `BcryptPasswordHasher` | Implementacion de PasswordHasher con pbkdf2_sha256 |
| `storage/local_storage.py` | `LocalDiskStorage` | Implementacion de FileStorage (disco local, UUID como nombre) |
| `storage/validators.py` | `PDFFileValidator` | Valida extension .pdf, MIME application/pdf, cabecera %PDF |
| `storage/validators.py` | `UnsupportedFileValidator` | Rechaza formatos no soportados |
| `storage/validators.py` | `SimpleFileValidatorFactory` | Fabrica que retorna el validador correcto segun el archivo |

### Capa de Interfaces (`interfaces/`)

| Archivo | Clase/Funcion | Descripcion |
|---------|---------------|-------------|
| `dependencies.py` | `get_user_repo()` | Inyecta SQLAlchemyUserRepository |
| `dependencies.py` | `get_enterprise_repo()` | Inyecta SQLAlchemyEnterpriseRepository |
| `dependencies.py` | `get_pdf_repo()` | Inyecta SQLAlchemyPDFRepository |
| `dependencies.py` | `get_password_hasher()` | Inyecta BcryptPasswordHasher |
| `dependencies.py` | `get_token_provider()` | Inyecta JoseJWTTokenProvider |
| `dependencies.py` | `get_storage()` | Inyecta LocalDiskStorage |
| `dependencies.py` | `get_validator_factory()` | Inyecta SimpleFileValidatorFactory |
| `dependencies.py` | `get_register_user_use_case()` | Compone el caso de uso RegisterUser |
| `dependencies.py` | `get_login_user_use_case()` | Compone el caso de uso LoginUser |
| `dependencies.py` | `get_upload_pdf_use_case()` | Compone el caso de uso ValidateAndUploadPDF |
| `dependencies.py` | `get_current_user()` | Extrae y valida el usuario del token JWT |
| `schemas/auth.py` | `CedulaStr` | Tipo Pydantic: regex `^[0-9]{6,12}$` |
| `schemas/auth.py` | `NitStr` | Tipo Pydantic: regex `^[0-9]{9,15}(-[0-9])?$` |
| `schemas/auth.py` | `RegisterRequest` | Schema de registro |
| `schemas/auth.py` | `LoginRequest` | Schema de login |
| `schemas/auth.py` | `AuthResponse` | Schema de respuesta de auth (token + datos) |
| `schemas/auth.py` | `UserResponse` | Schema de respuesta de usuario |
| `schemas/pdf.py` | `PDFUploadResponse` | Schema de respuesta de subida de PDF |
| `api_v1/router.py` | `api_router` | Router agregador |
| `api_v1/auth_routes.py` | `register()` | Endpoint POST /auth/register |
| `api_v1/auth_routes.py` | `login()` | Endpoint POST /auth/login |
| `api_v1/auth_routes.py` | `me()` | Endpoint GET /auth/me |
| `api_v1/pdf_routes.py` | `upload_pdf()` | Endpoint POST /documents/upload-pdf |

### Frontend

| Archivo | Funcion/Componente | Descripcion |
|---------|-------------------|-------------|
| `api/axiosClient.js` | `axiosClient` | Instancia Axios con interceptor que agrega `Authorization: Bearer <token>` |
| `api/authService.js` | `registerUser()` | POST /auth/register |
| `api/authService.js` | `loginUser()` | POST /auth/login |
| `api/authService.js` | `fetchProfile()` | GET /auth/me |
| `api/pdfService.js` | `uploadPdf()` | POST /documents/upload-pdf (multipart/form-data) |
| `context/AuthContext.jsx` | `AuthProvider` | Proveedor de contexto con token, user, signIn, signOut |
| `context/AuthContext.jsx` | `useAuthContext()` | Hook para consumir el contexto de autenticacion |
| `hooks/useAuthForm.js` | `useLoginForm()` | Hook de formulario de login con react-hook-form |
| `hooks/useAuthForm.js` | `useRegisterForm()` | Hook de formulario de registro |
| `hooks/useAuthForm.js` | `validations` | Reglas de validacion para cedula y NIT |
| `hooks/useUpload.js` | `useUpload()` | Hook que maneja subida de PDF (validacion MIME, estados, errores) |
| `pages/LoginPage.jsx` | `LoginPage` | Pagina de login con formulario de cedula + contraseña |
| `pages/RegisterPage.jsx` | `RegisterPage` | Pagina de registro con datos personales y de empresa |
| `pages/DashboardPage.jsx` | `DashboardPage` | Panel principal: info del usuario + formulario de subida de PDF |
| `components/Button.jsx` | `Button` | Boton estilizado con Tailwind |
| `components/Card.jsx` | `Card` | Tarjeta con titulo, subtitulo y contenido |
| `components/Input.jsx` | `Input` | Input con label, validacion y mensaje de error |
| `components/Layout.jsx` | `Layout` | Layout centrado responsivo |
| `App.jsx` | `App` | Definicion de rutas: /, /login, /register, /dashboard |
| `App.jsx` | `ProtectedRoute` | Componente que redirige a /login si no hay token |

---

## Flujo Principal de la Aplicacion

```text
1. REGISTRO
   Usuario llena formulario → POST /auth/register
   → Valida cedula (6-12 digitos) y NIT (9-15 digitos)
   → Crea empresa si no existe (por NIT)
   → Hashea contraseña con pbkdf2_sha256
   → Guarda usuario en MySQL

2. LOGIN
   Usuario ingresa cedula + contraseña → POST /auth/login
   → Busca usuario por cedula
   → Verifica contraseña hasheada
   → Genera JWT con expiracion configurable
   → Frontend almacena token en localStorage

3. SUBIDA DE PDF
   Usuario selecciona PDF → POST /documents/upload-pdf
   → Valida extension .pdf
   → Valida MIME application/pdf
   → Valida cabecera binaria %PDF
   → Ejecuta pipeline de 5 capas para encontrar la cedula:
      Capa 1: pypdf (texto nativo)
      Capa 2: pdfplumber (layouts complejos)
      Capa 3: PyMuPDF fitz (texto alternativo)
      Capa 4: OCR imagenes incrustadas (fotos dentro del PDF)
      Capa 5: OCR pagina completa (PDF escaneado)
   → Si encuentra la cedula: guarda en disco + registra en BD
   → Si NO encuentra: retorna error 400

4. SESION
   Cada peticion autenticada incluye header Authorization: Bearer <JWT>
   → El interceptor de Axios lo agrega automaticamente
   → FastAPI extrae el token, decodifica, busca usuario
   → Si expiro o es invalido: retorna 401
```

---

## Dependencias del Backend

| Paquete | Version | Proposito |
|---------|---------|-----------|
| `fastapi` | 0.116.1 | Framework web asincrono |
| `uvicorn[standard]` | 0.34.0 | Servidor ASGI |
| `sqlalchemy` | 2.0.39 | ORM para MySQL |
| `pymysql` | 1.1.1 | Driver MySQL para Python |
| `pypdf` | 5.3.0 | Extraccion de texto de PDFs (Capa 1) |
| `pdfplumber` | 0.11.4 | Extraccion de texto avanzada (Capa 2) |
| `pymupdf` | 1.26.4 | Renderizado de PDFs a imagenes + texto (Capas 3, 4, 5) |
| `pytesseract` | 0.3.13 | Wrapper Python para Tesseract OCR (Capas 4, 5) |
| `opencv-python-headless` | 4.12.0.88 | Preprocesamiento de imagenes para OCR |
| `numpy` | 2.2.3 | Manipulacion de arrays de pixeles |
| `Pillow` | 11.1.0 | Soporte de imagenes (dependencia de pytesseract) |
| `python-jose[cryptography]` | 3.3.0 | Creacion y verificacion de tokens JWT |
| `passlib[bcrypt]` | 1.7.4 | Hashing seguro de contraseñas |
| `python-multipart` | 0.0.20 | Soporte para subida de archivos multipart |
| `pydantic-settings` | 2.8.1 | Configuracion tipada con variables de entorno |

---

## Modelo de Base de Datos

```text
┌─────────────────────┐       ┌──────────────────────┐       ┌──────────────────────────┐
│    enterprises      │       │       users           │       │    pdf_documents          │
├─────────────────────┤       ├──────────────────────┤       ├──────────────────────────┤
│ id (PK)             │──┐    │ id (PK)              │──┐    │ id (PK)                  │
│ name                │  │    │ first_name           │  │    │ filename                 │
│ nit (UNIQUE, INDEX) │  │    │ last_name            │  │    │ mime_type                │
│ created_at          │  │    │ cedula (UNIQUE, IDX) │  │    │ storage_path             │
└─────────────────────┘  │    │ hashed_password      │  │    │ sha256                   │
                         └───▶│ enterprise_id (FK)   │  └───▶│ user_id (FK)             │
                              │ created_at           │       │ enterprise_id (FK)       │
                              └──────────────────────┘       │ created_at               │
                                                             └──────────────────────────┘
```

Las tablas se crean automaticamente al iniciar el servidor gracias a `Base.metadata.create_all(bind=engine)` en el evento `startup` de FastAPI.

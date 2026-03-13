# TaricAI

Motor de clasificación arancelaria TARIC con inteligencia artificial para agencias de aduanas e importadores en España.

## Tech Stack

- **Backend:** Python 3.12, FastAPI
- **Base de datos:** PostgreSQL 16
- **Vector DB:** Pinecone (embeddings OpenAI)
- **IA:** Claude API (Anthropic), OpenAI
- **Infraestructura:** Docker, Docker Compose

## Estructura del Proyecto

```
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/       # Endpoints
│   │   ├── core/      # Configuración
│   │   ├── db/        # Base de datos
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── schemas/   # Schemas Pydantic
│   │   └── services/  # Lógica de negocio
│   └── tests/
├── scrapers/          # Scripts de extracción TARIC
├── data/              # Datos TARIC y benchmarks
├── notebooks/         # Jupyter notebooks de exploración
└── docs/              # Documentación técnica
```

## Setup Rápido

```bash
# 1. Clonar y configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 2. Levantar con Docker
docker compose up -d

# 3. Verificar
curl http://localhost:8000/health
```

## Desarrollo Local (sin Docker)

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

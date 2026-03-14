"""
Servicio de embeddings y busqueda semantica con Pinecone + sentence-transformers.

Usa modelo local gratuito (all-MiniLM-L6-v2, 384 dims) para generar embeddings
e indexar las descripciones TARIC en Pinecone para busqueda semantica (RAG).
"""

import logging
from typing import Any

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

# Modelo local de embeddings (384 dimensiones, gratuito, rapido)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Singleton para no recargar el modelo cada vez
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Carga el modelo de embeddings (singleton)."""
    global _model
    if _model is None:
        logger.info(f"Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Modelo cargado correctamente")
    return _model


# Pinecone index config
INDEX_NAME = settings.pinecone_index_name
CLOUD = "aws"
REGION = "us-east-1"  # Free tier region


def get_pinecone_client() -> Pinecone:
    """Inicializa el cliente de Pinecone."""
    return Pinecone(api_key=settings.pinecone_api_key)


def ensure_index_exists() -> Any:
    """Crea el indice de Pinecone si no existe. Retorna el indice."""
    pc = get_pinecone_client()

    existing = pc.list_indexes().names()
    if INDEX_NAME not in existing:
        logger.info(f"Creando indice Pinecone: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=CLOUD, region=REGION),
        )
        logger.info(f"Indice {INDEX_NAME} creado correctamente")

    return pc.Index(INDEX_NAME)


def generate_embedding(text: str) -> list[float]:
    """Genera un vector embedding para un texto usando modelo local."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: list[str], batch_size: int = 256) -> list[list[float]]:
    """Genera embeddings para una lista de textos en batch."""
    model = get_embedding_model()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embeddings = model.encode(batch, normalize_embeddings=True, show_progress_bar=False)
        all_embeddings.extend(embeddings.tolist())

        if (i + batch_size) % 1000 == 0 or i + len(batch) >= len(texts):
            logger.info(f"  Embeddings generados: {i + len(batch)}/{len(texts)}")

    return all_embeddings


def index_taric_codes(
    codes: list[dict],
    batch_size: int = 100,
) -> int:
    """
    Indexa codigos TARIC en Pinecone.

    Args:
        codes: Lista de dicts con keys: code, description, chapter, section, duty_rate
        batch_size: Tamano de batch para upsert

    Returns:
        Numero de vectores indexados
    """
    index = ensure_index_exists()
    total_indexed = 0

    # Generar todos los embeddings primero (mas eficiente en batch)
    texts = [f"{c['code']} - {c['description']}" for c in codes]
    logger.info(f"Generando {len(texts)} embeddings...")
    all_embeddings = generate_embeddings_batch(texts, batch_size=256)

    # Upsert en Pinecone por batches
    for i in range(0, len(codes), batch_size):
        batch_codes = codes[i : i + batch_size]
        batch_embeddings = all_embeddings[i : i + batch_size]

        vectors = []
        for code_data, embedding in zip(batch_codes, batch_embeddings):
            vectors.append({
                "id": code_data["code"],
                "values": embedding,
                "metadata": {
                    "code": code_data["code"],
                    "description": code_data["description"],
                    "chapter": code_data.get("chapter", ""),
                    "section": code_data.get("section", ""),
                    "duty_rate": code_data.get("duty_rate", ""),
                },
            })

        index.upsert(vectors=vectors)
        total_indexed += len(vectors)

        if total_indexed % 1000 == 0 or total_indexed >= len(codes):
            logger.info(f"  Indexados en Pinecone: {total_indexed}/{len(codes)}")

    return total_indexed


async def semantic_search(
    query: str,
    top_k: int = 10,
    min_score: float = 0.3,
) -> list[dict]:
    """
    Busqueda semantica de codigos TARIC.

    Args:
        query: Descripcion del producto a buscar
        top_k: Numero maximo de resultados
        min_score: Score minimo de similitud

    Returns:
        Lista de matches con codigo, descripcion y score
    """
    index = ensure_index_exists()

    # Generar embedding de la query
    query_embedding = generate_embedding(query)

    # Buscar en Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    matches = []
    for match in results.get("matches", []):
        if match["score"] >= min_score:
            matches.append({
                "code": match["metadata"]["code"],
                "description": match["metadata"]["description"],
                "chapter": match["metadata"].get("chapter", ""),
                "section": match["metadata"].get("section", ""),
                "duty_rate": match["metadata"].get("duty_rate", ""),
                "similarity_score": match["score"],
            })

    return matches


def get_index_stats() -> dict:
    """Obtiene estadisticas del indice de Pinecone."""
    try:
        index = ensure_index_exists()
        stats = index.describe_index_stats()
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "dimension": stats.get("dimension", EMBEDDING_DIMENSION),
            "index_name": INDEX_NAME,
        }
    except Exception as e:
        return {"error": str(e)}

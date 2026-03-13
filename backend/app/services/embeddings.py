"""
Servicio de embeddings y búsqueda semántica con Pinecone + OpenAI.

Indexa las descripciones TARIC como vectores en Pinecone para
poder hacer búsqueda semántica (RAG) y mejorar la clasificación.
"""

import logging
from typing import Any

import openai
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings

logger = logging.getLogger(__name__)

# Modelo de embeddings (1536 dimensiones, barato y rápido)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Pinecone index config
INDEX_NAME = settings.pinecone_index_name
CLOUD = "aws"
REGION = "us-east-1"  # Free tier region


def get_pinecone_client() -> Pinecone:
    """Inicializa el cliente de Pinecone."""
    return Pinecone(api_key=settings.pinecone_api_key)


def get_openai_client() -> openai.OpenAI:
    """Inicializa el cliente de OpenAI."""
    return openai.OpenAI(api_key=settings.openai_api_key)


def ensure_index_exists() -> Any:
    """Crea el índice de Pinecone si no existe. Retorna el índice."""
    pc = get_pinecone_client()

    existing = pc.list_indexes().names()
    if INDEX_NAME not in existing:
        logger.info(f"Creando índice Pinecone: {INDEX_NAME}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=CLOUD, region=REGION),
        )
        logger.info(f"Índice {INDEX_NAME} creado correctamente")

    return pc.Index(INDEX_NAME)


def generate_embedding(text: str) -> list[float]:
    """Genera un vector embedding para un texto usando OpenAI."""
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def generate_embeddings_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Genera embeddings para una lista de textos en batch."""
    client = get_openai_client()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        logger.info(f"  Embeddings generados: {i + len(batch)}/{len(texts)}")

    return all_embeddings


def index_taric_codes(
    codes: list[dict],
    batch_size: int = 100,
) -> int:
    """
    Indexa códigos TARIC en Pinecone.

    Args:
        codes: Lista de dicts con keys: code, description, chapter, section, duty_rate
        batch_size: Tamaño de batch para upsert

    Returns:
        Número de vectores indexados
    """
    index = ensure_index_exists()
    total_indexed = 0

    for i in range(0, len(codes), batch_size):
        batch = codes[i : i + batch_size]

        # Generar embeddings para las descripciones
        texts = [
            f"{c['code']} - {c['description']}" for c in batch
        ]
        embeddings = generate_embeddings_batch(texts, batch_size=batch_size)

        # Preparar vectors para Pinecone
        vectors = []
        for code_data, embedding in zip(batch, embeddings):
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

        # Upsert en Pinecone
        index.upsert(vectors=vectors)
        total_indexed += len(vectors)
        logger.info(f"  Indexados: {total_indexed}/{len(codes)}")

    return total_indexed


async def semantic_search(
    query: str,
    top_k: int = 10,
    min_score: float = 0.5,
) -> list[dict]:
    """
    Búsqueda semántica de códigos TARIC.

    Args:
        query: Descripción del producto a buscar
        top_k: Número máximo de resultados
        min_score: Score mínimo de similitud

    Returns:
        Lista de matches con código, descripción y score
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
    """Obtiene estadísticas del índice de Pinecone."""
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

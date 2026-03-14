"""
Script para indexar todos los codigos TARIC en Pinecone.

Lee los codigos de PostgreSQL (ya cargados por taric_loader.py)
y genera embeddings locales con sentence-transformers para indexar en Pinecone.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.database import SessionLocal
from app.models.taric import TaricCode, Subheading, Heading, Chapter, Section
from app.services.embeddings import index_taric_codes, get_index_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_codes_from_db() -> list[dict]:
    """Carga todos los codigos TARIC declarables de PostgreSQL con su jerarquia."""
    db = SessionLocal()
    try:
        codes = []
        taric_codes = (
            db.query(TaricCode)
            .join(Subheading)
            .join(Heading)
            .join(Chapter)
            .join(Section)
            .all()
        )

        for tc in taric_codes:
            sh = tc.subheading
            h = sh.heading if sh else None
            ch = h.chapter if h else None
            sec = ch.section if ch else None

            codes.append({
                "code": tc.code,
                "description": tc.description_es or "",
                "chapter": ch.code if ch else "",
                "section": sec.roman_numeral if sec else "",
                "duty_rate": getattr(tc, "duty_rate", "") or "",
            })

        return codes
    finally:
        db.close()


def main():
    print("=== TaricAI Pinecone Indexer ===\n")

    # 1. Cargar codigos de PostgreSQL
    print("1. Cargando codigos de PostgreSQL...")
    codes = load_codes_from_db()
    print(f"   {len(codes)} codigos TARIC cargados\n")

    if not codes:
        print("ERROR: No hay codigos en la base de datos.")
        print("Ejecuta primero: python scrapers/taric_loader.py")
        return

    # 2. Indexar en Pinecone
    print("2. Generando embeddings e indexando en Pinecone...")
    print("   (modelo local all-MiniLM-L6-v2, 384 dims, gratuito)\n")
    total = index_taric_codes(codes, batch_size=100)

    # 3. Stats
    print(f"\n3. Indexacion completada: {total} vectores")
    stats = get_index_stats()
    print(f"   Stats del indice: {stats}")
    print("\nListo! El RAG ahora mejorara las clasificaciones.")


if __name__ == "__main__":
    main()

"""
Script para indexar datos TARIC en Pinecone.

Uso:
    python scrapers/index_pinecone.py              # Desde JSON scrapeado
    python scrapers/index_pinecone.py --from-db     # Desde PostgreSQL
    python scrapers/index_pinecone.py --test        # Solo capítulo 09 (test)
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.embeddings import index_taric_codes, get_index_stats


DATA_DIR = Path(__file__).parent.parent / "data" / "taric"


def load_codes_from_json(filename: str = "taric_nomenclature.json") -> list[dict]:
    """Carga códigos TARIC desde el JSON scrapeado."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"ERROR: No existe {filepath}")
        print("Ejecuta primero: python scrapers/eu_taric_scraper.py")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    codes = []
    for section in data.get("sections", []):
        section_roman = section.get("roman", "")
        for chapter in section.get("chapters", []):
            ch_code = chapter.get("code", "")
            for heading in chapter.get("headings", []):
                h_code = heading.get("code", "")
                h_desc = heading.get("description_en", "")

                # Indexar la partida (4 dígitos)
                if h_code and h_desc:
                    codes.append({
                        "code": h_code.ljust(10, "0"),
                        "description": h_desc,
                        "chapter": ch_code,
                        "section": section_roman,
                        "duty_rate": "",
                    })

                # Indexar commodities (6-10 dígitos)
                for commodity in heading.get("commodities", []):
                    c_code = commodity.get("code", "")
                    c_desc = commodity.get("description", "")
                    if c_code and c_desc and commodity.get("declarable", False):
                        codes.append({
                            "code": c_code.ljust(10, "0"),
                            "description": c_desc,
                            "chapter": ch_code,
                            "section": section_roman,
                            "duty_rate": "",
                        })

    return codes


def load_codes_from_db() -> list[dict]:
    """Carga códigos TARIC desde PostgreSQL."""
    from app.db.database import SessionLocal
    from app.models.taric import TaricCode, Subheading, Heading, Chapter, Section

    db = SessionLocal()
    codes = []

    try:
        # Cargar headings (4 dígitos) con sus relaciones
        headings = db.query(Heading).all()
        for h in headings:
            chapter = h.chapter
            section = chapter.section if chapter else None
            codes.append({
                "code": h.code.ljust(10, "0"),
                "description": h.description_es or h.description_en or "",
                "chapter": chapter.code if chapter else "",
                "section": section.roman_numeral if section else "",
                "duty_rate": "",
            })

        # Cargar subheadings (6 dígitos)
        subheadings = db.query(Subheading).all()
        for sh in subheadings:
            heading = sh.heading
            chapter = heading.chapter if heading else None
            section = chapter.section if chapter else None
            codes.append({
                "code": sh.code.ljust(10, "0"),
                "description": sh.description_es or sh.description_en or "",
                "chapter": chapter.code if chapter else "",
                "section": section.roman_numeral if section else "",
                "duty_rate": sh.duty_rate or "",
            })

        # Cargar taric codes (10 dígitos)
        taric_codes = db.query(TaricCode).all()
        for tc in taric_codes:
            sh = tc.subheading
            heading = sh.heading if sh else None
            chapter = heading.chapter if heading else None
            section = chapter.section if chapter else None
            codes.append({
                "code": tc.code,
                "description": tc.description_es or tc.description_en or "",
                "chapter": chapter.code if chapter else "",
                "section": section.roman_numeral if section else "",
                "duty_rate": tc.duty_rate or "",
            })
    finally:
        db.close()

    return codes


def main():
    print("=== TaricAI Pinecone Indexer ===\n")

    # Determinar fuente de datos
    if "--from-db" in sys.argv:
        print("Cargando códigos desde PostgreSQL...")
        codes = load_codes_from_db()
    elif "--test" in sys.argv:
        print("Modo test: cargando desde JSON de prueba...")
        codes = load_codes_from_json("taric_test_chapter09.json")
        if not codes:
            # Fallback: crear datos de test
            codes = [
                {"code": "0901210000", "description": "Coffee, roasted, not decaffeinated", "chapter": "09", "section": "II", "duty_rate": "7.5%"},
                {"code": "0901220000", "description": "Coffee, roasted, decaffeinated", "chapter": "09", "section": "II", "duty_rate": "9%"},
                {"code": "0902100000", "description": "Green tea in packages <= 3kg", "chapter": "09", "section": "II", "duty_rate": "3.2%"},
                {"code": "0902200000", "description": "Green tea in packages > 3kg", "chapter": "09", "section": "II", "duty_rate": "0%"},
                {"code": "0904110000", "description": "Pepper, neither crushed nor ground", "chapter": "09", "section": "II", "duty_rate": "0%"},
            ]
    else:
        print("Cargando códigos desde JSON scrapeado...")
        codes = load_codes_from_json()

    if not codes:
        print("No hay códigos para indexar. Ejecuta primero el scraper.")
        return

    print(f"Total códigos a indexar: {len(codes)}")
    print("\nIndexando en Pinecone...")

    indexed = index_taric_codes(codes)
    print(f"\n✅ Vectores indexados: {indexed}")

    # Mostrar stats
    stats = get_index_stats()
    print(f"\nEstadísticas del índice:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n¡Indexación completada!")


if __name__ == "__main__":
    main()

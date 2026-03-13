"""
Loader: carga datos TARIC scrapeados en PostgreSQL.

Lee el JSON generado por eu_taric_scraper (taric_nomenclature.json)
y lo inserta en las tablas de la base de datos.

Estructura del JSON:
  sections[] -> chapters[] -> headings[] -> commodities[]

Mapeo a tablas:
  Section (roman_numeral, title_es, title_en)
  Chapter (code 2 dig, description_es, section_id)
  Heading (code 4 dig, description_es, chapter_id)
  Subheading (code 6 dig, description_es, heading_id)
  TaricCode (code 10 dig, description_es, subheading_id)
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session

from app.db.database import SessionLocal, engine, Base
from app.models.taric import Section, Chapter, Heading, Subheading, TaricCode

DATA_DIR = Path(__file__).parent.parent / "data" / "taric"

# Mapeo seccion ID -> numeral romano
ROMAN_NUMERALS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
    8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII",
    14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX",
    20: "XX", 21: "XXI",
}


def load_full_nomenclature(db: Session, data: dict):
    """Carga toda la nomenclatura TARIC desde el JSON del scraper."""

    stats = {
        "sections": 0,
        "chapters": 0,
        "headings": 0,
        "subheadings": 0,
        "taric_codes": 0,
        "skipped_duplicates": 0,
    }

    for section_data in data.get("sections", []):
        # --- SECCION ---
        roman = section_data.get("roman", "")
        title_es = section_data.get("title_es", "")
        title_en = section_data.get("title_en", "")

        section = db.query(Section).filter_by(roman_numeral=roman).first()
        if not section:
            section = Section(
                roman_numeral=roman,
                title_es=title_es,
                title_en=title_en,
            )
            db.add(section)
            db.flush()
            stats["sections"] += 1
            print(f"  Seccion {roman}: {title_es[:50]}")

        for ch_data in section_data.get("chapters", []):
            # --- CAPITULO ---
            ch_code = ch_data.get("code", "")
            ch_desc = ch_data.get("description_en", "")

            chapter = db.query(Chapter).filter_by(code=ch_code).first()
            if not chapter:
                chapter = Chapter(
                    code=ch_code,
                    description_es=ch_desc,  # En ingles por ahora, AEAT enriquece despues
                    section_id=section.id,
                )
                db.add(chapter)
                db.flush()
                stats["chapters"] += 1

            for h_data in ch_data.get("headings", []):
                # --- PARTIDA (4 digitos) ---
                h_code = h_data.get("code", "")
                h_desc = h_data.get("description", "")

                heading = db.query(Heading).filter_by(code=h_code).first()
                if not heading:
                    heading = Heading(
                        code=h_code,
                        description_es=h_desc,
                        chapter_id=chapter.id,
                    )
                    db.add(heading)
                    db.flush()
                    stats["headings"] += 1

                # Procesar commodities -> Subheadings (6 dig) + TaricCodes (8-10 dig)
                # Primero recopilar subheadings unicos
                subheading_map = {}  # code_6dig -> Subheading

                for comm in h_data.get("commodities", []):
                    comm_code = comm.get("code", "").replace(" ", "")
                    comm_desc = comm.get("description", "")

                    if len(comm_code) < 6:
                        continue

                    # Extraer subheading (6 primeros digitos)
                    sh_code = comm_code[:6]

                    if sh_code not in subheading_map:
                        # Buscar o crear subheading
                        subheading = db.query(Subheading).filter_by(code=sh_code).first()
                        if not subheading:
                            # Usar la descripcion del commodity si el codigo coincide exactamente
                            sh_desc = comm_desc if comm_code[:6] == comm_code.rstrip("0")[:6] else ""
                            subheading = Subheading(
                                code=sh_code,
                                description_es=sh_desc or f"Subpartida {sh_code}",
                                heading_id=heading.id,
                            )
                            db.add(subheading)
                            db.flush()
                            stats["subheadings"] += 1
                        subheading_map[sh_code] = subheading

                    # Crear TaricCode (10 digitos) si es declarable/leaf
                    if len(comm_code) >= 8 and comm.get("declarable", False):
                        # Normalizar a 10 digitos
                        taric_code_str = comm_code.ljust(10, "0")[:10]
                        sh = subheading_map.get(sh_code)

                        if sh:
                            existing = db.query(TaricCode).filter_by(code=taric_code_str).first()
                            if not existing:
                                taric = TaricCode(
                                    code=taric_code_str,
                                    description_es=comm_desc,
                                    subheading_id=sh.id,
                                )
                                db.add(taric)
                                stats["taric_codes"] += 1
                            else:
                                stats["skipped_duplicates"] += 1

            # Commit por capitulo para no perder todo si falla
            db.commit()
            print(f"    Cap {ch_code}: {stats['headings']} headings, {stats['taric_codes']} codes total")

    return stats


def enrich_with_aeat(db: Session):
    """Enriquece los datos con descripciones en espanol de AEAT."""
    aeat_file = DATA_DIR / "aeat_nomenclature.json"

    if not aeat_file.exists():
        print("INFO: No hay datos AEAT disponibles. Saltando enriquecimiento.")
        return

    with open(aeat_file, "r", encoding="utf-8") as f:
        aeat_data = json.load(f)

    updated = 0
    for chapter_code, items in aeat_data.items():
        for item in items:
            code = item.get("code", "")
            desc_es = item.get("description_es", "")
            duty = item.get("duty_rate")

            if not code or not desc_es:
                continue

            if len(code) == 4:
                record = db.query(Heading).filter_by(code=code).first()
            elif len(code) == 6:
                record = db.query(Subheading).filter_by(code=code).first()
            elif len(code) >= 8:
                record = db.query(TaricCode).filter_by(code=code[:10]).first()
            else:
                continue

            if record:
                record.description_es = desc_es
                if duty and hasattr(record, "duty_rate"):
                    record.duty_rate = duty
                updated += 1

    db.commit()
    print(f"Registros enriquecidos con AEAT: {updated}")


def load_all():
    """Ejecuta el proceso completo de carga."""
    print("=== TaricAI Data Loader ===\n")

    nom_file = DATA_DIR / "taric_nomenclature.json"
    if not nom_file.exists():
        print("ERROR: No existe taric_nomenclature.json")
        print("Ejecuta primero: python scrapers/eu_taric_scraper.py")
        return

    # Create tables if they don't exist
    print("Creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)

    # Load JSON
    print(f"Leyendo {nom_file}...")
    with open(nom_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        print("\n1. Cargando nomenclatura completa...")
        stats = load_full_nomenclature(db, data)

        print("\n2. Enriqueciendo con datos AEAT...")
        enrich_with_aeat(db)

        # Print final stats
        print("\n" + "=" * 40)
        print("ESTADISTICAS FINALES")
        print("=" * 40)
        print(f"Secciones:    {db.query(Section).count()}")
        print(f"Capitulos:    {db.query(Chapter).count()}")
        print(f"Partidas:     {db.query(Heading).count()}")
        print(f"Subpartidas:  {db.query(Subheading).count()}")
        print(f"Codigos TARIC:{db.query(TaricCode).count()}")
        print(f"\nDuplicados saltados: {stats.get('skipped_duplicates', 0)}")
        print("\nCarga completada!")
    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_all()

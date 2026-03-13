"""
Loader: carga datos TARIC scrapeados en PostgreSQL.

Lee los JSON generados por eu_taric_scraper y aeat_scraper,
y los inserta en las tablas de la base de datos.
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


def load_sections(db: Session) -> dict[str, int]:
    """Carga las 21 secciones TARIC desde el JSON estático."""
    sections_file = DATA_DIR / "taric_sections.json"

    if not sections_file.exists():
        print("ERROR: No existe taric_sections.json. Ejecuta primero eu_taric_scraper.py")
        return {}

    with open(sections_file, "r", encoding="utf-8") as f:
        sections_data = json.load(f)

    section_map = {}  # roman -> id
    for s in sections_data:
        existing = db.query(Section).filter_by(roman_numeral=s["roman"]).first()
        if existing:
            section_map[s["roman"]] = existing.id
            continue

        section = Section(
            roman_numeral=s["roman"],
            title_es=s["title_es"],
            title_en=s["title_en"],
        )
        db.add(section)
        db.flush()
        section_map[s["roman"]] = section.id

    db.commit()
    print(f"Secciones cargadas: {len(section_map)}")
    return section_map


def load_nomenclature(db: Session, section_map: dict[str, int]):
    """Carga la nomenclatura completa desde el JSON de EU TARIC."""
    nom_file = DATA_DIR / "taric_nomenclature.json"

    if not nom_file.exists():
        print("ERROR: No existe taric_nomenclature.json. Ejecuta primero eu_taric_scraper.py")
        return

    with open(nom_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters_data = data.get("chapters", {})
    chapter_count = 0
    heading_count = 0

    for chapter_code, chapter_data in chapters_data.items():
        section_roman = chapter_data.get("section", "")
        section_id = section_map.get(section_roman)

        if not section_id:
            print(f"  WARN: Sección {section_roman} no encontrada para capítulo {chapter_code}")
            continue

        # Crear o buscar capítulo
        existing_ch = db.query(Chapter).filter_by(code=chapter_code).first()
        if not existing_ch:
            ch = Chapter(
                code=chapter_code,
                description_es=f"Capítulo {chapter_code}",
                section_id=section_id,
            )
            db.add(ch)
            db.flush()
            chapter_id = ch.id
            chapter_count += 1
        else:
            chapter_id = existing_ch.id

        # Cargar partidas del capítulo
        for h in chapter_data.get("headings", []):
            code = h.get("code", "")
            desc = h.get("description", "")

            if len(code) == 4:
                existing_h = db.query(Heading).filter_by(code=code).first()
                if not existing_h:
                    heading = Heading(
                        code=code,
                        description_es=desc,
                        chapter_id=chapter_id,
                    )
                    db.add(heading)
                    heading_count += 1
            elif len(code) == 6:
                # Find parent heading
                parent_code = code[:4]
                parent = db.query(Heading).filter_by(code=parent_code).first()
                if parent:
                    existing_sh = db.query(Subheading).filter_by(code=code).first()
                    if not existing_sh:
                        subheading = Subheading(
                            code=code,
                            description_es=desc,
                            heading_id=parent.id,
                        )
                        db.add(subheading)
            elif len(code) == 10:
                # Find parent subheading
                parent_code = code[:6]
                parent = db.query(Subheading).filter_by(code=parent_code).first()
                if parent:
                    existing_tc = db.query(TaricCode).filter_by(code=code).first()
                    if not existing_tc:
                        taric = TaricCode(
                            code=code,
                            description_es=desc,
                            subheading_id=parent.id,
                        )
                        db.add(taric)

    db.commit()
    print(f"Capítulos cargados: {chapter_count}")
    print(f"Partidas cargadas: {heading_count}")


def enrich_with_aeat(db: Session):
    """Enriquece los datos con descripciones en español de AEAT."""
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

            # Update matching records with Spanish descriptions
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

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("1. Cargando secciones...")
        section_map = load_sections(db)

        if not section_map:
            print("No se pudieron cargar las secciones. Abortando.")
            return

        print("\n2. Cargando nomenclatura EU TARIC...")
        load_nomenclature(db, section_map)

        print("\n3. Enriqueciendo con datos AEAT...")
        enrich_with_aeat(db)

        # Print stats
        print("\n=== Estadísticas ===")
        print(f"Secciones:   {db.query(Section).count()}")
        print(f"Capítulos:   {db.query(Chapter).count()}")
        print(f"Partidas:    {db.query(Heading).count()}")
        print(f"Subpartidas: {db.query(Subheading).count()}")
        print(f"Códigos 10d: {db.query(TaricCode).count()}")
        print("\n¡Carga completada!")
    finally:
        db.close()


if __name__ == "__main__":
    load_all()

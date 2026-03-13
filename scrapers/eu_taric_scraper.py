"""
Scraper para datos TARIC usando la UK Trade Tariff API v2.

La UK Trade Tariff API es una REST API pública (sin auth) que devuelve JSON
estructurado. Los códigos HS/CN son compartidos con EU TARIC (misma base).

Fuente principal para prototipado. Para producción, usar CIRCABC Excel extractions.

Endpoints:
- GET /api/v2/sections              → 21 secciones
- GET /api/v2/sections/{id}         → detalle sección + capítulos
- GET /api/v2/headings/{code}       → partida + subpartidas + commodities
- GET /api/v2/commodities/{code}    → código completo con duties
"""

import json
import time
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent.parent / "data" / "taric"
API_BASE = "https://www.trade-tariff.service.gov.uk/api/v2"

# Las 21 secciones TARIC con títulos en español (referencia estática)
TARIC_SECTIONS_ES = {
    1: "Animales vivos y productos del reino animal",
    2: "Productos del reino vegetal",
    3: "Grasas y aceites animales o vegetales",
    4: "Productos de las industrias alimentarias; bebidas, líquidos alcohólicos y vinagre; tabaco",
    5: "Productos minerales",
    6: "Productos de las industrias químicas o de las industrias conexas",
    7: "Plástico y sus manufacturas; caucho y sus manufacturas",
    8: "Pieles, cueros, peletería y manufacturas de estas materias",
    9: "Madera, carbón vegetal y manufacturas de madera; corcho y sus manufacturas",
    10: "Pasta de madera o de las demás materias fibrosas celulósicas; papel o cartón",
    11: "Materias textiles y sus manufacturas",
    12: "Calzado, sombreros y demás tocados, paraguas, quitasoles, bastones",
    13: "Manufacturas de piedra, yeso, cemento, amianto, mica; productos cerámicos; vidrio",
    14: "Perlas, piedras preciosas, metales preciosos; bisutería; monedas",
    15: "Metales comunes y sus manufacturas",
    16: "Máquinas y aparatos, material eléctrico y sus partes",
    17: "Material de transporte",
    18: "Instrumentos y aparatos de óptica, fotografía, medida, control, precisión; relojería; instrumentos musicales",
    19: "Armas, municiones y sus partes y accesorios",
    20: "Mercancías y productos diversos",
    21: "Objetos de arte o colección y antigüedades",
}

ROMAN_NUMERALS = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
    8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII",
    14: "XIV", 15: "XV", 16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX",
    20: "XX", 21: "XXI",
}

SESSION = requests.Session()
SESSION.headers.update({"Accept": "application/json"})


def fetch_sections() -> list[dict]:
    """Obtiene las 21 secciones desde la API."""
    resp = SESSION.get(f"{API_BASE}/sections", timeout=30)
    resp.raise_for_status()
    sections = resp.json()

    result = []
    for s in sections:
        section_id = s["id"]
        result.append({
            "id": section_id,
            "roman": ROMAN_NUMERALS.get(section_id, str(section_id)),
            "title_en": s.get("title", ""),
            "title_es": TARIC_SECTIONS_ES.get(section_id, ""),
            "chapter_from": s.get("chapter_from", ""),
            "chapter_to": s.get("chapter_to", ""),
        })

    return result


def fetch_section_chapters(section_id: int) -> list[dict]:
    """Obtiene los capítulos de una sección."""
    resp = SESSION.get(f"{API_BASE}/sections/{section_id}", timeout=30)
    resp.raise_for_status()
    data = resp.json()

    chapters = []
    for ch in data.get("chapters", []):
        chapters.append({
            "goods_nomenclature_item_id": ch.get("goods_nomenclature_item_id", ""),
            "description": ch.get("description", ""),
            "chapter_note": ch.get("chapter_note", ""),
        })

    return chapters


def fetch_heading(heading_code: str) -> dict:
    """Obtiene una partida con sus subpartidas y commodities."""
    resp = SESSION.get(f"{API_BASE}/headings/{heading_code}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_commodity(commodity_code: str) -> dict:
    """Obtiene un código commodity con sus duties y medidas."""
    resp = SESSION.get(f"{API_BASE}/commodities/{commodity_code}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_commodities_from_heading(heading_data: dict) -> list[dict]:
    """Extrae los commodities de la respuesta de una partida."""
    commodities = []

    for c in heading_data.get("commodities", []):
        code = c.get("goods_nomenclature_item_id", "")
        commodities.append({
            "code": code,
            "description": c.get("description", ""),
            "leaf": c.get("leaf", False),
            "declarable": c.get("declarable", False),
            "product_line_suffix": c.get("producline_suffix", "80"),
        })

    return commodities


def download_all_nomenclature(delay: float = 0.3) -> dict:
    """Descarga toda la nomenclatura: secciones → capítulos → partidas → commodities."""
    print("Descargando secciones...")
    sections = fetch_sections()

    all_data = {
        "source": "UK Trade Tariff API v2",
        "note": "HS/CN codes shared with EU TARIC",
        "sections": [],
    }

    for section in sections:
        print(f"\nSección {section['roman']}: {section['title_es'][:60]}...")
        section_data = {
            **section,
            "chapters": [],
        }

        chapters = fetch_section_chapters(section["id"])
        time.sleep(delay)

        for ch in chapters:
            ch_code = ch["goods_nomenclature_item_id"][:2]
            print(f"  Capítulo {ch_code}: {ch['description'][:50]}...")

            chapter_data = {
                "code": ch_code,
                "description_en": ch["description"],
                "headings": [],
            }

            # Obtener partidas del capítulo (4 dígitos)
            # La API organiza por heading (4 dígitos)
            try:
                # Get all headings for this chapter
                # Headings are XX01 to XX99 where XX is the chapter
                heading_list = _get_chapter_headings(ch_code, delay)
                chapter_data["headings"] = heading_list
            except Exception as e:
                print(f"    Error en capítulo {ch_code}: {e}")

            section_data["chapters"].append(chapter_data)

        all_data["sections"].append(section_data)

    return all_data


def _get_chapter_headings(chapter_code: str, delay: float) -> list[dict]:
    """Obtiene todas las partidas de un capítulo con sus commodities."""
    headings = []

    # Try heading codes from XX01 to XX99
    for i in range(100):
        heading_code = f"{chapter_code}{i:02d}"
        try:
            data = fetch_heading(heading_code)
            time.sleep(delay)

            commodities = extract_commodities_from_heading(data)
            headings.append({
                "code": heading_code,
                "description_en": data.get("description", ""),
                "commodities": commodities,
            })
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                continue  # Heading doesn't exist, skip
            raise

    return headings


def save_data(data: dict, filename: str = "taric_nomenclature.json") -> Path:
    """Guarda la nomenclatura en JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nDatos guardados en {output_path}")
    return output_path


def save_sections_json() -> Path:
    """Guarda las secciones como referencia estática."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "taric_sections.json"

    sections = fetch_sections()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)

    print(f"Secciones guardadas en {output_path}")
    return output_path


def download_single_chapter(chapter_code: str) -> dict:
    """Descarga un solo capítulo (útil para testing)."""
    print(f"Descargando capítulo {chapter_code}...")
    headings = _get_chapter_headings(chapter_code, delay=0.3)

    result = {
        "code": chapter_code,
        "headings": headings,
        "total_commodities": sum(len(h["commodities"]) for h in headings),
    }

    print(f"  → {len(headings)} partidas, {result['total_commodities']} commodities")
    return result


if __name__ == "__main__":
    import sys

    print("=== TaricAI EU TARIC Scraper (UK Trade Tariff API) ===\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode: download only chapter 09 (coffee, tea, spices)
        print("Modo test: descargando solo capítulo 09...")
        data = download_single_chapter("09")
        save_data({"test_chapter": data}, "taric_test_chapter09.json")
    elif len(sys.argv) > 1 and sys.argv[1] == "--sections":
        save_sections_json()
    else:
        # Full download
        data = download_all_nomenclature()
        save_data(data)

    print("\n¡Completado!")

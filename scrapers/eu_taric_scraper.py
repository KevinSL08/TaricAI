"""
Scraper para datos TARIC usando la UK Trade Tariff API v2 (JSON:API format).

La UK Trade Tariff API es una REST API pública (sin auth) que devuelve JSON:API.
Los códigos HS/CN son compartidos con EU TARIC (misma base).

Endpoints:
- GET /api/v2/sections              → 21 secciones
- GET /api/v2/sections/{id}         → detalle sección + capítulos (included)
- GET /api/v2/headings/{code}       → partida + commodities (included)
- GET /api/v2/commodities/{code}    → código completo con duties
"""

import json
import time
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent.parent / "data" / "taric"
API_BASE = "https://www.trade-tariff.service.gov.uk/api/v2"

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
    """Obtiene las 21 secciones desde la API (JSON:API format)."""
    resp = SESSION.get(f"{API_BASE}/sections", timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    result = []
    for item in raw.get("data", []):
        attrs = item.get("attributes", {})
        section_id = attrs.get("id", int(item["id"]))
        result.append({
            "id": section_id,
            "roman": attrs.get("numeral", ROMAN_NUMERALS.get(section_id, "")),
            "title_en": attrs.get("title", ""),
            "title_es": TARIC_SECTIONS_ES.get(section_id, ""),
            "chapter_from": attrs.get("chapter_from", ""),
            "chapter_to": attrs.get("chapter_to", ""),
        })

    return result


def fetch_section_chapters(section_id: int) -> list[dict]:
    """Obtiene los capítulos de una sección (desde included)."""
    resp = SESSION.get(f"{API_BASE}/sections/{section_id}", timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    chapters = []
    for item in raw.get("included", []):
        if item.get("type") != "chapter":
            continue
        attrs = item.get("attributes", {})
        code = attrs.get("goods_nomenclature_item_id", "")[:2]
        chapters.append({
            "code": code,
            "goods_nomenclature_item_id": attrs.get("goods_nomenclature_item_id", ""),
            "description": attrs.get("formatted_description", attrs.get("description", "")),
            "headings_from": attrs.get("headings_from", ""),
            "headings_to": attrs.get("headings_to", ""),
        })

    return chapters


def fetch_heading(heading_code: str) -> dict:
    """Obtiene una partida con sus commodities (JSON:API)."""
    resp = SESSION.get(f"{API_BASE}/headings/{heading_code}", timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    # Extract heading info
    attrs = raw.get("data", {}).get("attributes", {})
    heading = {
        "code": heading_code,
        "description": attrs.get("formatted_description", attrs.get("description", "")),
    }

    # Extract commodities from included
    commodities = []
    for item in raw.get("included", []):
        if item.get("type") != "commodity":
            continue
        c_attrs = item.get("attributes", {})
        commodities.append({
            "code": c_attrs.get("goods_nomenclature_item_id", ""),
            "description": c_attrs.get("formatted_description", c_attrs.get("description", "")),
            "leaf": c_attrs.get("leaf", False),
            "declarable": c_attrs.get("declarable", False),
        })

    heading["commodities"] = commodities
    return heading


def fetch_commodity(commodity_code: str) -> dict:
    """Obtiene un código commodity con sus duties y medidas."""
    resp = SESSION.get(f"{API_BASE}/commodities/{commodity_code}", timeout=30)
    resp.raise_for_status()
    return resp.json()


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
        section_data = {**section, "chapters": []}

        chapters = fetch_section_chapters(section["id"])
        time.sleep(delay)

        for ch in chapters:
            ch_code = ch["code"]
            print(f"  Capítulo {ch_code}: {ch['description'][:50]}...")

            chapter_data = {
                "code": ch_code,
                "description_en": ch["description"],
                "headings": [],
            }

            try:
                heading_list = _get_chapter_headings(ch_code, ch.get("headings_from", ""), ch.get("headings_to", ""), delay)
                chapter_data["headings"] = heading_list
            except Exception as e:
                print(f"    Error en capítulo {ch_code}: {e}")

            section_data["chapters"].append(chapter_data)

        all_data["sections"].append(section_data)

    return all_data


def _get_chapter_headings(chapter_code: str, headings_from: str, headings_to: str, delay: float) -> list[dict]:
    """Obtiene las partidas de un capítulo usando el rango de headings."""
    headings = []

    # Parse range from API (e.g. "0901" to "0910")
    if headings_from and headings_to:
        start = int(headings_from)
        end = int(headings_to)
    else:
        start = int(f"{chapter_code}01")
        end = int(f"{chapter_code}99")

    for code_int in range(start, end + 1):
        heading_code = f"{code_int:04d}"
        try:
            heading = fetch_heading(heading_code)
            time.sleep(delay)
            headings.append(heading)
            n_comm = len(heading.get("commodities", []))
            if n_comm > 0:
                print(f"    {heading_code}: {heading['description'][:40]}... ({n_comm} commodities)")
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                continue
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

    # Get chapter heading range from sections
    sections = fetch_sections()
    headings_from = f"{chapter_code}01"
    headings_to = f"{chapter_code}99"

    # Try to find the actual range
    for section in sections:
        chapters = fetch_section_chapters(section["id"])
        for ch in chapters:
            if ch["code"] == chapter_code:
                headings_from = ch.get("headings_from", headings_from)
                headings_to = ch.get("headings_to", headings_to)
                break

    headings = _get_chapter_headings(chapter_code, headings_from, headings_to, delay=0.3)

    result = {
        "code": chapter_code,
        "headings": headings,
        "total_commodities": sum(len(h.get("commodities", [])) for h in headings),
    }

    print(f"  -> {len(headings)} partidas, {result['total_commodities']} commodities")
    return result


if __name__ == "__main__":
    import sys

    print("=== TaricAI EU TARIC Scraper (UK Trade Tariff API) ===\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Modo test: descargando solo capítulo 09 (café, té, especias)...")
        data = download_single_chapter("09")
        save_data({"test_chapter": data}, "taric_test_chapter09.json")
    elif len(sys.argv) > 1 and sys.argv[1] == "--sections":
        save_sections_json()
    else:
        data = download_all_nomenclature()
        save_data(data)

    print("\n¡Completado!")

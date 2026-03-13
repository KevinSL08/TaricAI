"""
Scraper para AEAT CLASS - Sistema de clasificación arancelaria español.

Fuente: Web service SOAP de la AEAT (Agencia Tributaria)
URL: https://www2.agenciatributaria.gob.es/ADUA/internet/es/aeat/dit/adu/adws/jaxws/TrfConsNomenclatura.html

Complementa los datos EU TARIC con descripciones oficiales en español
y notas específicas de la administración aduanera española.
"""

import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data" / "taric"

# AEAT SOAP web service para consulta de nomenclatura
AEAT_WS_URL = "https://www2.agenciatributaria.gob.es/ADUA/internet/ws/AREAConsNomenclaturas"

# AEAT CLASS web interface
AEAT_CLASS_URL = "https://www2.agenciatributaria.gob.es/ADUA/internet/es/aeat/dit/adu/adws/jaxws/TrfConsNomenclatura.html"


def build_soap_request(goods_code: str, date: str = "") -> str:
    """Construye el XML SOAP para consultar la nomenclatura AEAT."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:trf="http://www.agenciatributaria.gob.es/ADUA/internet/ws">
  <soapenv:Body>
    <trf:consultaNomenclatura>
      <trf:codigoMercancia>{goods_code}</trf:codigoMercancia>
      <trf:fecha>{date}</trf:fecha>
    </trf:consultaNomenclatura>
  </soapenv:Body>
</soapenv:Envelope>"""


def query_aeat_nomenclature(goods_code: str) -> dict | None:
    """Consulta la nomenclatura AEAT via SOAP web service."""
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "consultaNomenclatura",
    }

    try:
        resp = requests.post(
            AEAT_WS_URL,
            data=build_soap_request(goods_code),
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error querying AEAT for {goods_code}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "lxml-xml")
    result = {}

    # Parse SOAP response
    code_elem = soup.find("codigoMercancia")
    desc_elem = soup.find("descripcion")
    duty_elem = soup.find("derechoArancelario")

    if code_elem:
        result["code"] = code_elem.text
    if desc_elem:
        result["description_es"] = desc_elem.text
    if duty_elem:
        result["duty_rate"] = duty_elem.text

    return result if result else None


def scrape_aeat_chapter(chapter_code: str, delay: float = 0.5) -> list[dict]:
    """Scrape todas las subpartidas de un capítulo desde AEAT."""
    results = []

    # Consultar el capítulo base
    data = query_aeat_nomenclature(chapter_code)
    if data:
        results.append(data)

    # Consultar partidas (4 dígitos)
    for i in range(100):
        heading_code = f"{chapter_code}{i:02d}"
        data = query_aeat_nomenclature(heading_code)
        if data:
            results.append(data)
        time.sleep(delay)

    return results


def download_aeat_data(chapters: list[str], delay: float = 0.5) -> dict:
    """Descarga datos de AEAT para los capítulos indicados."""
    all_data = {}

    for chapter in chapters:
        print(f"Consultando AEAT capítulo {chapter}...")
        results = scrape_aeat_chapter(chapter, delay)
        all_data[chapter] = results
        print(f"  → {len(results)} resultados")

    return all_data


def save_aeat_data(data: dict, filename: str = "aeat_nomenclature.json"):
    """Guarda los datos AEAT en JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Datos AEAT guardados en {output_path}")
    return output_path


if __name__ == "__main__":
    # Test con capítulo 09 (café, té, mate, especias)
    print("=== TaricAI AEAT Scraper ===")
    print("Consultando capítulo 09 como prueba...")
    test_data = download_aeat_data(["09"])
    save_aeat_data(test_data, "aeat_test_chapter09.json")
    print("\n¡Test completado!")

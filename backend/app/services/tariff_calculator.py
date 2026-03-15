"""
Servicio de calculo de aranceles usando UK Trade Tariff API.

Obtiene datos reales de aranceles de la API oficial y calcula:
- Arancel base (ad-valorem, especifico o mixto)
- IVA espanol (21% general, 10% reducido, 4% superreducido)
- Coste total de importacion
"""

import logging
import re
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

API_BASE = "https://www.trade-tariff.service.gov.uk/api/v2"

# Cache en memoria: {commodity_code: (timestamp, parsed_data)}
_measures_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 3600  # 1 hora

# Tipos de IVA espanol
IVA_RATES = {
    "general": 21.0,
    "reducido": 10.0,
    "superreducido": 4.0,
}

# Tipos de medida de importacion relevantes
IMPORT_MEASURE_TYPES = {
    "103",  # Third country duty
    "105",  # Non preferential tariff quota
    "106",  # Preferential tariff quota
    "142",  # Tariff preference
    "143",  # Tariff preference (condition-based)
    "145",  # Preferential tariff quota (condition-based)
    "112",  # Autonomous tariff suspension
}


def _try_fetch_commodity(code: str) -> dict | None:
    """Intenta obtener datos de un commodity. Retorna None si 404."""
    url = f"{API_BASE}/commodities/{code}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        return None


def _find_declarable_code_via_heading(commodity_code: str) -> dict | None:
    """
    Busca un codigo declarable a traves del heading (4 digitos).

    La UK Trade Tariff API no acepta todos los codigos TARIC de 10 digitos de la EU.
    Buscamos en el heading y encontramos el codigo declarable mas cercano.
    """
    heading_code = commodity_code[:4]
    url = f"{API_BASE}/headings/{heading_code}"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        data = response.json()

        included = data.get("included", [])
        commodities = [
            c for c in included
            if c.get("type") == "commodity"
            and c.get("attributes", {}).get("declarable") is True
        ]

        if not commodities:
            return None

        # Buscar el commodity cuyo goods_nomenclature_item_id sea mas parecido
        target = commodity_code.ljust(10, "0")
        best_match = None
        best_prefix_len = 0

        for c in commodities:
            c_code = c.get("attributes", {}).get(
                "goods_nomenclature_item_id", ""
            )
            # Contar prefijo comun
            prefix_len = 0
            for a, b in zip(target, c_code):
                if a == b:
                    prefix_len += 1
                else:
                    break

            if prefix_len > best_prefix_len:
                best_prefix_len = prefix_len
                best_match = c_code

        if best_match:
            logger.info(
                f"Codigo {commodity_code} mapeado a {best_match} (UK declarable)"
            )
            return _try_fetch_commodity(best_match)

        return None

    except requests.exceptions.RequestException:
        return None


def fetch_commodity_data(commodity_code: str) -> dict:
    """
    Obtiene datos de commodity de UK Trade Tariff API.

    Estrategia de busqueda (los codigos TARIC EU no siempre coinciden con UK):
    1. Intentar codigo original de 10 digitos
    2. Intentar codigo de 8 digitos (sin sufijo TARIC)
    3. Buscar via heading (4 digitos) y encontrar el codigo declarable mas cercano
    """
    # Verificar cache
    if commodity_code in _measures_cache:
        ts, cached_data = _measures_cache[commodity_code]
        if time.time() - ts < CACHE_TTL:
            logger.debug(f"Cache hit para {commodity_code}")
            return cached_data

    logger.info(f"Buscando aranceles para codigo {commodity_code}")

    # Estrategia 1: codigo completo 10d
    data = _try_fetch_commodity(commodity_code)

    # Estrategia 2: codigo 8d (sin ultimos 2 digitos TARIC)
    if not data and len(commodity_code) == 10:
        code_8d = commodity_code[:8] + "00"
        if code_8d != commodity_code:
            logger.info(f"Probando con 8 digitos: {code_8d}")
            data = _try_fetch_commodity(code_8d)

    # Estrategia 3: buscar via heading
    if not data:
        logger.info(f"Buscando via heading para {commodity_code}")
        data = _find_declarable_code_via_heading(commodity_code)

    if not data:
        raise ValueError(
            f"Codigo {commodity_code} no encontrado en la UK Trade Tariff API. "
            "Verifica que sea un codigo TARIC valido y declarable."
        )

    # Guardar en cache
    _measures_cache[commodity_code] = (time.time(), data)
    return data


def _build_included_lookup(included: list[dict]) -> dict[tuple[str, str], dict]:
    """Construye un dict de lookup {(type, id): object} del array included de JSON:API."""
    return {(obj["type"], obj["id"]): obj for obj in included}


def parse_import_measures(api_response: dict) -> list[dict]:
    """
    Parsea el response JSON:API y extrae medidas de importacion.

    Retorna lista de dicts con: measure_type, duty_expression, geographical_area, duty_amount
    """
    data = api_response.get("data", {})
    included = api_response.get("included", [])
    lookup = _build_included_lookup(included)

    # Obtener IDs de import_measures
    import_measure_refs = (
        data.get("relationships", {})
        .get("import_measures", {})
        .get("data", [])
    )

    measures = []
    for ref in import_measure_refs:
        measure_key = (ref["type"], ref["id"])
        measure_obj = lookup.get(measure_key)
        if not measure_obj:
            continue

        attrs = measure_obj.get("attributes", {})
        relationships = measure_obj.get("relationships", {})

        # Obtener tipo de medida
        measure_type_ref = relationships.get("measure_type", {}).get("data")
        measure_type_desc = "Unknown"
        measure_type_id = ""
        if measure_type_ref:
            mt_key = (measure_type_ref["type"], measure_type_ref["id"])
            mt_obj = lookup.get(mt_key)
            if mt_obj:
                measure_type_desc = mt_obj.get("attributes", {}).get("description", "Unknown")
                measure_type_id = mt_obj.get("attributes", {}).get("measure_type_series_id", "")

        # Obtener area geografica
        geo_ref = relationships.get("geographical_area", {}).get("data")
        geo_desc = "Desconocido"
        geo_id = ""
        if geo_ref:
            geo_key = (geo_ref["type"], geo_ref["id"])
            geo_obj = lookup.get(geo_key)
            if geo_obj:
                geo_desc = geo_obj.get("attributes", {}).get("description", "Desconocido")
                geo_id = geo_obj.get("attributes", {}).get("geographical_area_id", "")

        # Obtener expresion de arancel de duty_expression
        duty_expr_ref = relationships.get("duty_expression", {}).get("data")
        duty_expression = ""
        if duty_expr_ref:
            de_key = (duty_expr_ref["type"], duty_expr_ref["id"])
            de_obj = lookup.get(de_key)
            if de_obj:
                duty_expression = de_obj.get("attributes", {}).get("base", "")
                if not duty_expression:
                    duty_expression = de_obj.get("attributes", {}).get(
                        "formatted_base", ""
                    )

        # Si no hay duty_expression en el objeto dedicado, buscar en measure_components
        if not duty_expression:
            mc_refs = relationships.get("measure_components", {}).get("data", [])
            parts = []
            for mc_ref in mc_refs:
                mc_key = (mc_ref["type"], mc_ref["id"])
                mc_obj = lookup.get(mc_key)
                if mc_obj:
                    mc_attrs = mc_obj.get("attributes", {})
                    duty_amount = mc_attrs.get("duty_amount")
                    duty_expression_id = mc_attrs.get("duty_expression_id", "")
                    measurement_unit = mc_attrs.get("measurement_unit_code", "")
                    measurement_unit_qualifier = mc_attrs.get(
                        "measurement_unit_qualifier_code", ""
                    )

                    if duty_amount is not None:
                        if duty_expression_id in ("01", "04"):
                            # Ad-valorem (percentage)
                            parts.append(f"{duty_amount} %")
                        elif measurement_unit:
                            parts.append(
                                f"{duty_amount} EUR/{measurement_unit}"
                            )
                        else:
                            parts.append(f"{duty_amount} %")

            duty_expression = " + ".join(parts) if parts else "Free"

        measures.append({
            "measure_type": measure_type_desc,
            "measure_type_id": measure_type_id,
            "duty_expression": duty_expression.strip() if duty_expression else "Free",
            "geographical_area": geo_desc,
            "geographical_area_id": geo_id,
        })

    return measures


def resolve_duty_for_origin(
    measures: list[dict], origin_country: str | None
) -> dict:
    """
    Selecciona la medida arancelaria aplicable segun el pais de origen.

    Prioridad:
    1. Medida especifica para el pais de origen
    2. ERGA OMNES (arancel de tercer pais, por defecto)
    3. Primera medida disponible
    """
    if not measures:
        return {
            "measure_type": "Sin datos",
            "duty_expression": "No disponible",
            "geographical_area": "N/A",
            "geographical_area_id": "",
        }

    # Filtrar solo medidas relevantes de importacion (third country duty, preferences)
    third_country = [
        m for m in measures
        if "third country" in m["measure_type"].lower()
        or "duty" in m["measure_type"].lower()
    ]

    # Si hay pais de origen, buscar medida especifica
    if origin_country:
        country_upper = origin_country.upper()
        # Buscar preferencia especifica para el pais
        for m in measures:
            if m["geographical_area_id"] == country_upper:
                return m

    # Buscar ERGA OMNES (ID = "1011") en medidas de tercer pais
    for m in third_country:
        if m["geographical_area_id"] == "1011":
            return m

    # Buscar cualquier ERGA OMNES
    for m in measures:
        if m["geographical_area_id"] == "1011":
            return m

    # Fallback: primera medida de tercer pais o primera medida
    return third_country[0] if third_country else measures[0]


def parse_duty_expression(
    expression: str,
    customs_value: float,
    weight_kg: float | None = None,
) -> tuple[float, str]:
    """
    Parsea una expresion de arancel y calcula el importe.

    Formatos soportados:
    - "6.00 %" → ad-valorem
    - "27.5 EUR/100 kg" → especifico
    - "12.8% + 27.5 EUR/100 kg" → mixto
    - "Free" / "0.00 %" → libre

    Retorna: (importe_eur, rate_str_humanizado)
    """
    if not expression or expression.strip().lower() in ("free", "0", "0.0", ""):
        return 0.0, "0% (Libre)"

    total = 0.0
    rate_parts = []

    # Separar por + para aranceles mixtos
    parts = re.split(r'\s*\+\s*', expression)

    for part in parts:
        part = part.strip()

        # Ad-valorem: "6.00 %" o "6.00%" o "6%"
        ad_valorem_match = re.search(r'(\d+\.?\d*)\s*%', part)
        # Especifico: "27.5 EUR/100 kg" o "1.6 EUR / 100 kg" o "EUR 27.5/100 kg"
        specific_match = re.search(
            r'(\d+\.?\d*)\s*EUR\s*/\s*(\d+\.?\d*)\s*(\w+)',
            part, re.IGNORECASE
        )
        # Especifico sin divisor: "1.6 EUR/kg"
        specific_simple = re.search(
            r'(\d+\.?\d*)\s*EUR\s*/\s*(\w+)',
            part, re.IGNORECASE
        )

        if specific_match:
            amount = float(specific_match.group(1))
            divisor = float(specific_match.group(2))
            unit = specific_match.group(3).lower()

            if weight_kg and unit in ("kg", "kgs"):
                duty = (weight_kg / divisor) * amount
                total += duty
                rate_parts.append(f"{amount} EUR/{int(divisor)} kg")
            else:
                # Sin peso, no podemos calcular especificos
                rate_parts.append(f"{amount} EUR/{int(divisor)} {unit} (peso requerido)")

        elif specific_simple and not ad_valorem_match:
            amount = float(specific_simple.group(1))
            unit = specific_simple.group(2).lower()

            if weight_kg and unit in ("kg", "kgs"):
                duty = weight_kg * amount
                total += duty
                rate_parts.append(f"{amount} EUR/kg")
            else:
                rate_parts.append(f"{amount} EUR/{unit} (peso requerido)")

        elif ad_valorem_match:
            pct = float(ad_valorem_match.group(1))
            duty = customs_value * (pct / 100.0)
            total += duty
            rate_parts.append(f"{pct}%")

    rate_str = " + ".join(rate_parts) if rate_parts else expression
    return round(total, 2), rate_str


async def calculate_import_duties(
    commodity_code: str,
    origin_country: str | None = None,
    customs_value_eur: float = 0.0,
    weight_kg: float | None = None,
    iva_type: str = "general",
) -> dict[str, Any]:
    """
    Calcula los aranceles de importacion para un codigo TARIC.

    Flujo:
    1. Obtener datos de UK Trade Tariff API
    2. Parsear medidas de importacion
    3. Seleccionar medida aplicable segun pais de origen
    4. Calcular arancel
    5. Aplicar IVA espanol
    6. Retornar desglose completo
    """
    # 1. Fetch data from API
    api_data = fetch_commodity_data(commodity_code)

    # Obtener descripcion del commodity
    commodity_desc = (
        api_data.get("data", {})
        .get("attributes", {})
        .get("formatted_description", "")
    )
    if not commodity_desc:
        commodity_desc = (
            api_data.get("data", {})
            .get("attributes", {})
            .get("description", "Sin descripcion")
        )
    # Limpiar tags HTML de la descripcion
    commodity_desc = re.sub(r'<[^>]+>', '', commodity_desc)

    # Verificar si es declarable
    declarable = (
        api_data.get("data", {})
        .get("attributes", {})
        .get("declarable", True)
    )

    notes = None
    if not declarable:
        notes = (
            "Este codigo no es declarable (no es un codigo hoja). "
            "Es posible que necesite un codigo mas especifico."
        )

    # 2. Parse measures
    all_measures = parse_import_measures(api_data)

    if not all_measures:
        logger.warning(f"No se encontraron medidas para {commodity_code}")
        # Retornar con arancel 0 y nota
        iva_rate = IVA_RATES.get(iva_type, 21.0)
        iva_amount = round(customs_value_eur * (iva_rate / 100), 2)
        return {
            "commodity_code": commodity_code,
            "commodity_description": commodity_desc,
            "origin_country": origin_country,
            "customs_value_eur": customs_value_eur,
            "duty_rate": "No disponible",
            "duty_amount_eur": 0.0,
            "iva_type": iva_type,
            "iva_rate_pct": iva_rate,
            "iva_base_eur": customs_value_eur,
            "iva_amount_eur": iva_amount,
            "total_import_cost_eur": round(customs_value_eur + iva_amount, 2),
            "applicable_measure": {
                "measure_type": "Sin datos",
                "duty_expression": "No disponible",
                "geographical_area": "N/A",
            },
            "all_measures": [],
            "source": "uk-trade-tariff-api",
            "notes": "No se encontraron medidas arancelarias para este codigo.",
        }

    # 3. Resolve duty for origin
    applicable = resolve_duty_for_origin(all_measures, origin_country)

    # 4. Calculate duty
    duty_amount, duty_rate_str = parse_duty_expression(
        applicable["duty_expression"], customs_value_eur, weight_kg
    )

    # 5. Apply Spanish IVA
    iva_rate = IVA_RATES.get(iva_type, 21.0)
    iva_base = customs_value_eur + duty_amount
    iva_amount = round(iva_base * (iva_rate / 100), 2)

    # 6. Total
    total = round(customs_value_eur + duty_amount + iva_amount, 2)

    # Formatear medidas para el response
    all_measures_info = [
        {
            "measure_type": m["measure_type"],
            "duty_expression": m["duty_expression"],
            "geographical_area": m["geographical_area"],
        }
        for m in all_measures
    ]

    return {
        "commodity_code": commodity_code,
        "commodity_description": commodity_desc,
        "origin_country": origin_country,
        "customs_value_eur": customs_value_eur,
        "duty_rate": duty_rate_str,
        "duty_amount_eur": duty_amount,
        "iva_type": iva_type,
        "iva_rate_pct": iva_rate,
        "iva_base_eur": round(iva_base, 2),
        "iva_amount_eur": iva_amount,
        "total_import_cost_eur": total,
        "applicable_measure": {
            "measure_type": applicable["measure_type"],
            "duty_expression": applicable["duty_expression"],
            "geographical_area": applicable["geographical_area"],
        },
        "all_measures": all_measures_info,
        "source": "uk-trade-tariff-api",
        "notes": notes,
    }

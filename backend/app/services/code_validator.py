"""
Servicio de validacion y correccion de codigos TARIC contra PostgreSQL.

Estrategia: Longest Prefix Match
1. Si el codigo exacto existe en DB -> usarlo
2. Si no, buscar el codigo valido con el prefijo mas largo en comun
3. Esto corrige subcodigos inventados por el LLM manteniendo la maxima precision
"""

import logging

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.taric import TaricCode

logger = logging.getLogger(__name__)

# Cache simple para evitar queries repetidas
_code_cache: dict[str, str | None] = {}
_heading_cache: dict[str, list[str]] = {}


def _get_codes_for_prefix(db: Session, prefix: str) -> list[str]:
    """Obtiene todos los codigos validos que empiezan con el prefijo dado."""
    if prefix in _heading_cache:
        return _heading_cache[prefix]

    codes = (
        db.query(TaricCode.code)
        .filter(TaricCode.code.like(f"{prefix}%"))
        .order_by(TaricCode.code)
        .all()
    )
    result = [c[0] for c in codes]
    _heading_cache[prefix] = result
    return result


def validate_and_correct_code(
    predicted_code: str,
    product_description: str = "",
    rag_codes: list[str] | None = None,
) -> dict:
    """
    Valida un codigo TARIC contra la base de datos y lo corrige si no existe.

    Estrategia Longest Prefix Match:
    1. Si el codigo exacto existe -> OK
    2. Buscar todos los codigos validos bajo el mismo prefijo progresivamente
    3. Elegir el que tiene el prefijo mas largo en comun con el predicho
    4. Si hay empate, preferir codigos de RAG, luego el mas generico

    Returns:
        dict con: code, corrected (bool), original_code, description, method
    """
    if not predicted_code or len(predicted_code) < 4:
        return {
            "code": predicted_code,
            "corrected": False,
            "original_code": predicted_code,
            "description": "",
            "method": "invalid_input",
        }

    code_10 = predicted_code.ljust(10, "0")[:10]

    # Check cache
    if code_10 in _code_cache:
        cached = _code_cache[code_10]
        if cached == code_10:
            return {"code": code_10, "corrected": False, "original_code": predicted_code, "description": "", "method": "cache_exact"}
        elif cached:
            return {"code": cached, "corrected": True, "original_code": predicted_code, "description": "", "method": "cache_corrected"}

    db = SessionLocal()
    try:
        # 1. Verificar si el codigo exacto existe
        exact = db.query(TaricCode).filter_by(code=code_10).first()
        if exact:
            _code_cache[code_10] = code_10
            return {
                "code": code_10,
                "corrected": False,
                "original_code": predicted_code,
                "description": exact.description_es or "",
                "method": "exact_match",
            }

        # 2. Longest Prefix Match: probar prefijos de 9 a 4 digitos
        rag_set = set(rag_codes) if rag_codes else set()

        for prefix_len in range(9, 3, -1):
            prefix = code_10[:prefix_len]
            valid_codes = _get_codes_for_prefix(db, prefix)

            if not valid_codes:
                continue

            # Si solo hay un codigo bajo este prefijo, es la respuesta
            if len(valid_codes) == 1:
                result_code = valid_codes[0]
                _code_cache[code_10] = result_code
                tc = db.query(TaricCode).filter_by(code=result_code).first()
                return {
                    "code": result_code,
                    "corrected": True,
                    "original_code": predicted_code,
                    "description": tc.description_es if tc else "",
                    "method": f"prefix_{prefix_len}_unique",
                }

            # Multiples candidatos: priorizar
            # a) Codigo exacto del RAG
            rag_matches = [c for c in valid_codes if c in rag_set]
            if rag_matches:
                # Elegir el RAG match con prefijo mas largo en comun
                best_rag = max(rag_matches, key=lambda c: _common_prefix_len(c, code_10))
                _code_cache[code_10] = best_rag
                tc = db.query(TaricCode).filter_by(code=best_rag).first()
                return {
                    "code": best_rag,
                    "corrected": True,
                    "original_code": predicted_code,
                    "description": tc.description_es if tc else "",
                    "method": f"prefix_{prefix_len}_rag",
                }

            # b) Codigo con mas digitos en comun
            best = max(valid_codes, key=lambda c: (
                _common_prefix_len(c, code_10),  # Mas digitos en comun
                -abs(int(c) - int(code_10)),      # Mas cercano numericamente
            ))
            _code_cache[code_10] = best
            tc = db.query(TaricCode).filter_by(code=best).first()
            return {
                "code": best,
                "corrected": True,
                "original_code": predicted_code,
                "description": tc.description_es if tc else "",
                "method": f"prefix_{prefix_len}_closest",
            }

        # 3. Nada encontrado - devolver original
        _code_cache[code_10] = code_10
        return {
            "code": code_10,
            "corrected": False,
            "original_code": predicted_code,
            "description": "",
            "method": "no_valid_match",
        }

    finally:
        db.close()


def _common_prefix_len(a: str, b: str) -> int:
    """Cuenta cuantos caracteres comparten de prefijo."""
    count = 0
    for ca, cb in zip(a, b):
        if ca == cb:
            count += 1
        else:
            break
    return count

"""
Servicio de clasificación TARIC usando Claude API.

Envía la descripción del producto a Claude con un prompt especializado
en clasificación arancelaria TARIC, y devuelve sugerencias de códigos.
"""

import json
import logging

import anthropic

from app.core.config import settings
from app.schemas.classification import ClassifyResponse, TaricSuggestion

logger = logging.getLogger(__name__)

# System prompt especializado en clasificación TARIC
TARIC_SYSTEM_PROMPT = """Eres un experto en clasificación arancelaria TARIC de la Unión Europea.
Tu trabajo es clasificar productos según la nomenclatura TARIC (basada en el Sistema Armonizado HS).

REGLAS DE CLASIFICACIÓN:
1. Sigue las Reglas Generales de Interpretación (RGI) del Sistema Armonizado
2. Clasifica primero por materia constitutiva, luego por función/uso
3. Los códigos TARIC tienen hasta 10 dígitos: Capítulo(2) + Partida(4) + Subpartida SA(6) + NC(8) + TARIC(10)
4. Proporciona SIEMPRE el código más específico posible (mínimo 6 dígitos, idealmente 8-10)
5. Si hay ambigüedad, proporciona múltiples opciones ordenadas por probabilidad

ESTRUCTURA DE TU RESPUESTA:
Responde SIEMPRE en JSON válido con esta estructura exacta:
{
  "suggestions": [
    {
      "code": "XXXXXXXXXX",
      "description": "Descripción oficial del código",
      "confidence": 0.95,
      "reasoning": "Explicación de por qué este código aplica",
      "duty_rate": "tasa si la conoces o null",
      "chapter": "XX",
      "section": "numeral romano"
    }
  ],
  "notes": "Notas adicionales o advertencias si las hay"
}

EJEMPLOS:
- "Café tostado en grano, arábica" → 0901 21 00 (Sección II, Capítulo 09)
- "Camiseta de algodón para hombre" → 6109 10 00 (Sección XI, Capítulo 61)
- "iPhone 15 Pro" → 8517 13 00 (Sección XVI, Capítulo 85)
- "Aceite de oliva virgen extra" → 1509 10 (Sección III, Capítulo 15)

Proporciona entre 1 y 5 sugerencias, ordenadas de mayor a menor confianza.
El campo "confidence" debe reflejar tu certeza real (0.0 a 1.0).
"""


def _build_user_prompt(
    description: str,
    origin_country: str | None = None,
    additional_context: str | None = None,
) -> str:
    """Construye el prompt del usuario para la clasificación."""
    prompt = f"Clasifica el siguiente producto según la nomenclatura TARIC:\n\n"
    prompt += f"**Producto:** {description}\n"

    if origin_country:
        prompt += f"**País de origen:** {origin_country}\n"

    if additional_context:
        prompt += f"**Contexto adicional:** {additional_context}\n"

    prompt += "\nResponde SOLO con el JSON válido, sin texto adicional."
    return prompt


def _parse_claude_response(response_text: str) -> dict:
    """Parsea la respuesta de Claude extrayendo el JSON."""
    # Intentar parsear directamente
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Buscar JSON dentro de bloques de código
    if "```json" in response_text:
        start = response_text.index("```json") + 7
        end = response_text.index("```", start)
        return json.loads(response_text[start:end].strip())

    if "```" in response_text:
        start = response_text.index("```") + 3
        end = response_text.index("```", start)
        return json.loads(response_text[start:end].strip())

    # Buscar el primer { y último }
    start = response_text.index("{")
    end = response_text.rindex("}") + 1
    return json.loads(response_text[start:end])


async def _get_rag_context(description: str) -> str:
    """Obtiene contexto RAG de Pinecone si está disponible."""
    if not settings.pinecone_api_key:
        return ""

    try:
        from app.services.embeddings import semantic_search

        matches = await semantic_search(description, top_k=5, min_score=0.6)
        if not matches:
            return ""

        context = "\n\nCÓDIGOS TARIC RELEVANTES (búsqueda semántica):\n"
        for m in matches:
            context += f"- {m['code']}: {m['description']} (similitud: {m['similarity_score']:.2f})\n"

        return context
    except Exception as e:
        logger.warning(f"RAG no disponible: {e}")
        return ""


async def classify_product(
    description: str,
    origin_country: str | None = None,
    additional_context: str | None = None,
) -> ClassifyResponse:
    """
    Clasifica un producto usando Claude API + RAG (Pinecone).

    Flujo:
    1. Busca códigos similares en Pinecone (si disponible)
    2. Incluye los resultados como contexto en el prompt
    3. Claude clasifica con el contexto enriquecido

    Args:
        description: Descripción del producto
        origin_country: Código ISO del país de origen
        additional_context: Contexto adicional

    Returns:
        ClassifyResponse con las sugerencias de clasificación
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Obtener contexto RAG
    rag_context = await _get_rag_context(description)

    user_prompt = _build_user_prompt(description, origin_country, additional_context)
    if rag_context:
        user_prompt += rag_context

    logger.info(f"Clasificando: {description[:80]}...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=TARIC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    response_text = message.content[0].text
    logger.debug(f"Respuesta Claude: {response_text[:200]}...")

    # Parsear respuesta
    try:
        parsed = _parse_claude_response(response_text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parseando respuesta de Claude: {e}")
        # Fallback: devolver respuesta raw como nota
        return ClassifyResponse(
            product_description=description,
            suggestions=[
                TaricSuggestion(
                    code="0000000000",
                    description="No se pudo parsear la clasificación",
                    confidence=0.0,
                    reasoning=response_text[:500],
                )
            ],
            top_code="0000000000",
            top_confidence=0.0,
            notes=f"Error parsing: {str(e)}. Respuesta raw disponible en reasoning.",
            source="claude-ai-error",
        )

    # Construir respuesta estructurada
    suggestions = []
    for s in parsed.get("suggestions", []):
        suggestions.append(
            TaricSuggestion(
                code=s.get("code", "").replace(" ", ""),
                description=s.get("description", ""),
                confidence=float(s.get("confidence", 0.5)),
                reasoning=s.get("reasoning", ""),
                duty_rate=s.get("duty_rate"),
                chapter=s.get("chapter"),
                section=s.get("section"),
            )
        )

    # Ordenar por confianza descendente
    suggestions.sort(key=lambda x: x.confidence, reverse=True)

    if not suggestions:
        suggestions = [
            TaricSuggestion(
                code="0000000000",
                description="No se encontraron sugerencias",
                confidence=0.0,
                reasoning="Claude no devolvió sugerencias válidas",
            )
        ]

    return ClassifyResponse(
        product_description=description,
        suggestions=suggestions,
        top_code=suggestions[0].code,
        top_confidence=suggestions[0].confidence,
        notes=parsed.get("notes"),
        source="claude-ai+rag" if rag_context else "claude-ai",
    )

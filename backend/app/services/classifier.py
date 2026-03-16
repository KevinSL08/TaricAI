"""
Servicio de clasificación TARIC con triple fallback de IA.

Flujo:
1. Intenta clasificar con Google Gemini (GRATUITO, tier generoso)
2. Si falla, usa Claude API (Anthropic) como fallback
3. Si falla, usa OpenAI GPT-4o como último recurso
4. Opcionalmente enriquece con RAG (Pinecone) si está disponible
"""

import json
import logging

import anthropic
import google.generativeai as genai
import openai

from app.core.config import settings
from app.schemas.classification import ClassifyResponse, TaricSuggestion

logger = logging.getLogger(__name__)

# System prompt especializado en clasificación TARIC
TARIC_SYSTEM_PROMPT = """Eres un despachante de aduanas experto con 30+ anos de experiencia en clasificacion arancelaria TARIC de la Union Europea.
Tu trabajo es clasificar productos segun la nomenclatura TARIC (basada en el Sistema Armonizado HS).

REGLAS GENERALES DE INTERPRETACION (RGI):
1. RGI-1: Los titulos de secciones y capitulos son solo orientativos. La clasificacion se determina por los textos de las partidas y notas de seccion/capitulo.
2. RGI-2a: Cualquier referencia a un articulo incluye el articulo incompleto o sin terminar, siempre que presente las caracteristicas esenciales.
3. RGI-2b: Cualquier referencia a una materia incluye las mezclas o combinaciones con otras materias.
4. RGI-3: Cuando un producto pueda clasificarse en dos o mas partidas:
   a) La partida mas especifica tiene prioridad sobre la mas general
   b) Los productos mezclados se clasifican segun la materia que les confiera el caracter esencial
   c) En ultima instancia, se clasifica en la partida con numeracion mas alta
5. RGI-6: La clasificacion en subpartidas se determina por los textos de las subpartidas y las notas de subpartida.

REGLAS CRITICAS DE CLASIFICACION:
- Los codigos DEBEN tener EXACTAMENTE 10 digitos. Si el codigo tiene menos de 10, completar con ceros a la derecha.
- SIEMPRE verifica el capitulo correcto ANTES de elegir subpartidas.
- Para APARATOS ELECTRICOS/ELECTRONICOS: si un producto funciona con electricidad (motor electrico, bateria recargable), clasificar en Seccion XVI (Cap 84-85), NO en la seccion del producto manual equivalente.
- Para ALIMENTOS: distinguir entre productos primarios (Cap 1-14) y preparaciones alimenticias (Cap 16-21).
- CHOCOLATE con cacao: SIEMPRE Cap 18 (1806), NO Cap 17 (1704 es confiteria SIN cacao).
- PINTURAS: acuosas (base agua/acrilicas) = 3209, no acuosas (base disolvente) = 3208.
- El ENVASE no cambia la clasificacion del contenido.
- Para CALZADO deportivo: distinguir entre suela (caucho/plastico) y parte superior (textil/cuero).

ESTRUCTURA DE TU RESPUESTA:
Responde SIEMPRE en JSON valido con esta estructura exacta:
{
  "suggestions": [
    {
      "code": "XXXXXXXXXX",
      "description": "Descripcion oficial del codigo",
      "confidence": 0.95,
      "reasoning": "Explicacion de por que este codigo aplica, citando RGI si es relevante",
      "duty_rate": "tasa si la conoces o null",
      "chapter": "XX",
      "section": "numeral romano"
    }
  ],
  "notes": "Notas adicionales o advertencias"
}

EJEMPLOS DE CLASIFICACION CORRECTA (codigos EXACTOS de 10 digitos):
- "Cafe tostado en grano arabica" -> 0901210000 (Cap 09)
- "Camiseta de algodon hombre" -> 6109100010 (Cap 61, T-shirts=6109100010)
- "iPhone 15 Pro" -> 8517130000 (Cap 85)
- "Aceite de oliva virgen extra" -> 1509200010 (Cap 15, EXTRA virgin=150920, other virgin=150940)
- "Chocolate con leche tableta sin relleno" -> 1806310000 (Cap 18, sin relleno=180631, con relleno=180632, NO 1704)
- "Cepillo dientes electrico" -> 8509800000 (Cap 85, electrico=Seccion XVI)
- "Pintura acrilica paredes base agua" -> 3209100000 (Cap 32, acuosa=3209)
- "TV LED 55 pulgadas" -> 8528721000 (Cap 85)
- "Salmon fresco Atlantico" -> 0302140010 (Cap 03, Atlantic salmon=0302140010)
- "Whisky escoces single malt" -> 2208303000 (Cap 22, single malt Scotch=2208303000)
- "Pila alcalina AA" -> 8506101800 (Cap 85)
- "Memoria USB flash" -> 8523511000 (Cap 85, semiconductor media=8523511000)
- "Aceite girasol refinado" -> 1512191000 (Cap 15)
- "Azucar blanco refinado" -> 1701991000 (Cap 17)
- "Mochila nylon portatil" -> 4202921100 (Cap 42, textile travel bags=4202921100)
- "Miel natural flores" -> 0409000090 (Cap 04, miel no manuka=0409000090)
- "Panuelos papel tissue caja" -> 4818201000 (Cap 48, handkerchiefs/facial tissues=4818201000)
- "Silla oficina ergonomica con ruedas" -> 9401310000 (Cap 94, silla tapizada con ruedas=9401310000)
- "Naranjas frescas" -> 0805108010 (Cap 08, fresh oranges=0805108010)
- "Aspirina comprimidos" -> 3004900000 (Cap 30, otros medicamentos=3004900000)
- "Almendras peladas" -> 0802121000 (Cap 08, shelled almonds=0802121000)
- "Auriculares bluetooth" -> 8518300090 (Cap 85, headphones other=8518300090)
- "Gafas sol polarizadas" -> 9004109100 (Cap 90, polarizing sunglasses=9004109100)
- "Juguete peluche oso" -> 9503003500 (Cap 95, stuffed toys=9503003500)
- "Impresora laser multifuncion" -> 8443321000 (Cap 84, multifuncion=844332, solo impresora=844331)
- "Motocicleta 125cc motor gasolina" -> 8711201000 (Cap 87, 50-250cc=871120, 250-500cc=871130)
- "Tornillos acero inoxidable" -> 7318159511 (Cap 73, tornillos/pernos acero inox=731815)
- "Reloj pulsera digital" -> 9102210000 (Cap 91, digital=910221, analogico=910211)
- "Cable USB datos" -> 8544421000 (Cap 85, cables electricos con conectores=854442)
- "Bicicleta montana adulto" -> 8712003010 (Cap 87, bicicletas sin motor=8712)

IMPORTANTE:
- Proporciona entre 1 y 5 sugerencias, ordenadas de mayor a menor confianza.
- El campo "confidence" debe reflejar tu certeza real (0.0 a 1.0).
- TODOS los codigos deben tener EXACTAMENTE 10 digitos.
- Si hay codigos TARIC relevantes proporcionados como contexto, USALOS para validar tu clasificacion.
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


def _parse_llm_response(response_text: str) -> dict:
    """Parsea la respuesta del LLM extrayendo el JSON."""
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

        matches = await semantic_search(description, top_k=10, min_score=0.35)
        if not matches:
            return ""

        context = "\n\nCODIGOS TARIC RELEVANTES (de la base de datos oficial, usa estos como referencia para validar tu clasificacion):\n"
        for m in matches:
            context += f"- {m['code']} | {m['description']} | Cap {m.get('chapter','')} | Sec {m.get('section','')} | sim={m['similarity_score']:.2f}\n"

        return context
    except Exception as e:
        logger.warning(f"RAG no disponible: {e}")
        return ""


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """Llama a Groq API (GRATUITO, 1000 req/dia) usando endpoint compatible OpenAI."""
    client = openai.OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2048,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Llama a Google Gemini API (GRATUITO) con fallback entre modelos."""
    genai.configure(api_key=settings.gemini_api_key)

    # Intentar varios modelos Gemini gratuitos en orden
    models_to_try = [
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
    ]

    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
            )
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.2,
                ),
            )
            logger.info(f"Gemini modelo {model_name} respondió OK")
            return response.text
        except Exception as e:
            logger.warning(f"Gemini {model_name} falló: {e}")
            last_error = e
            continue

    raise last_error or Exception("Todos los modelos Gemini fallaron")


def _call_claude(system_prompt: str, user_prompt: str) -> str:
    """Llama a Claude API y devuelve el texto de respuesta."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_openai(system_prompt: str, user_prompt: str) -> str:
    """Llama a OpenAI GPT-4o y devuelve el texto de respuesta."""
    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


async def classify_product(
    description: str,
    origin_country: str | None = None,
    additional_context: str | None = None,
) -> ClassifyResponse:
    """
    Clasifica un producto usando Claude API + RAG (Pinecone).
    Si Claude falla, usa OpenAI GPT-4o como fallback.

    Flujo:
    1. Busca códigos similares en Pinecone (si disponible)
    2. Incluye los resultados como contexto en el prompt
    3. Intenta Claude → si falla → OpenAI GPT-4o

    Args:
        description: Descripción del producto
        origin_country: Código ISO del país de origen
        additional_context: Contexto adicional

    Returns:
        ClassifyResponse con las sugerencias de clasificación
    """
    # Obtener contexto RAG
    rag_context = await _get_rag_context(description)

    user_prompt = _build_user_prompt(description, origin_country, additional_context)
    if rag_context:
        user_prompt += rag_context

    logger.info(f"Clasificando: {description[:80]}...")

    # Fallback chain: Groq (gratis) → Gemini (gratis) → Claude → OpenAI
    response_text = None
    source = "none"

    # 1. Groq (GRATUITO - Llama 3.3 70B, 1000 req/dia, ultra rapido)
    if settings.groq_api_key:
        try:
            response_text = _call_groq(TARIC_SYSTEM_PROMPT, user_prompt)
            source = "groq-llama"
            logger.info("Clasificación con Groq OK")
        except Exception as e:
            logger.warning(f"Groq falló ({e}), intentando Gemini...")

    # 2. Google Gemini (GRATUITO - tier generoso)
    if response_text is None and settings.gemini_api_key:
        try:
            response_text = _call_gemini(TARIC_SYSTEM_PROMPT, user_prompt)
            source = "gemini-flash"
            logger.info("Clasificación con Gemini OK")
        except Exception as e:
            logger.warning(f"Gemini falló ({e}), intentando Claude...")

    # 3. Claude (Anthropic) como fallback
    if response_text is None and settings.anthropic_api_key:
        try:
            response_text = _call_claude(TARIC_SYSTEM_PROMPT, user_prompt)
            source = "claude-ai"
            logger.info("Clasificación con Claude OK")
        except Exception as e:
            logger.warning(f"Claude falló ({e}), intentando OpenAI...")

    # 4. OpenAI GPT-4o como último recurso
    if response_text is None and settings.openai_api_key:
        try:
            response_text = _call_openai(TARIC_SYSTEM_PROMPT, user_prompt)
            source = "openai-gpt4o"
            logger.info("Clasificación con OpenAI OK")
        except Exception as e:
            logger.error(f"OpenAI también falló: {e}")

    if response_text is None:
        return ClassifyResponse(
            product_description=description,
            suggestions=[
                TaricSuggestion(
                    code="0000000000",
                    description="No hay servicio de IA disponible",
                    confidence=0.0,
                    reasoning="Ni Claude ni OpenAI pudieron procesar la solicitud. Verifica las API keys y créditos.",
                )
            ],
            top_code="0000000000",
            top_confidence=0.0,
            notes="Error: ningún proveedor de IA disponible",
            source="none",
        )

    if rag_context:
        source += "+rag"

    # Parsear respuesta
    try:
        parsed = _parse_llm_response(response_text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parseando respuesta: {e}")
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
            source=f"{source}-error",
        )

    # Extraer codigos RAG para validacion
    rag_codes = []
    if rag_context:
        for line in rag_context.split("\n"):
            if line.startswith("- ") and "|" in line:
                rag_code = line.split("|")[0].replace("- ", "").strip()
                if rag_code.isdigit():
                    rag_codes.append(rag_code)

    # Construir respuesta estructurada con validacion contra DB
    from app.services.code_validator import validate_and_correct_code

    suggestions = []
    for s in parsed.get("suggestions", []):
        # Normalizar codigo a exactamente 10 digitos
        raw_code = s.get("code", "").replace(" ", "").replace(".", "")
        if raw_code and raw_code.isdigit():
            raw_code = raw_code.ljust(10, "0")[:10]
        elif raw_code:
            raw_code = "".join(c for c in raw_code if c.isdigit())
            raw_code = raw_code.ljust(10, "0")[:10]

        # Validar y corregir contra la base de datos
        if raw_code and raw_code != "0000000000":
            validation = validate_and_correct_code(
                raw_code, description, rag_codes
            )
            validated_code = validation["code"]
            reasoning = s.get("reasoning", "")
            if validation["corrected"]:
                reasoning += f" [Codigo corregido de {validation['original_code']} a {validated_code} por validacion DB ({validation['method']})]"
                logger.info(f"Codigo corregido: {raw_code} -> {validated_code} ({validation['method']})")
        else:
            validated_code = raw_code or "0000000000"
            reasoning = s.get("reasoning", "")

        suggestions.append(
            TaricSuggestion(
                code=validated_code,
                description=s.get("description", ""),
                confidence=float(s.get("confidence", 0.5)),
                reasoning=reasoning,
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
                reasoning="El LLM no devolvió sugerencias válidas",
            )
        ]

    return ClassifyResponse(
        product_description=description,
        suggestions=suggestions,
        top_code=suggestions[0].code,
        top_confidence=suggestions[0].confidence,
        notes=parsed.get("notes"),
        source=source,
    )

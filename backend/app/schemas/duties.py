"""Schemas Pydantic para el calculador de aranceles."""

from pydantic import BaseModel, Field


class DutyCalculationRequest(BaseModel):
    """Request para calcular aranceles de importacion."""

    commodity_code: str = Field(
        ...,
        min_length=6,
        max_length=10,
        description="Codigo TARIC (6-10 digitos)",
        examples=["0805100020", "8471300000"],
    )
    origin_country: str | None = Field(
        None,
        min_length=2,
        max_length=2,
        description="Codigo ISO 3166-1 alpha-2 del pais de origen",
        examples=["CN", "MA", "US"],
    )
    customs_value_eur: float = Field(
        ...,
        gt=0,
        description="Valor en aduana en EUR (CIF)",
        examples=[10000.0],
    )
    weight_kg: float | None = Field(
        None,
        gt=0,
        description="Peso en kg (necesario para aranceles especificos)",
        examples=[500.0],
    )
    iva_type: str = Field(
        default="general",
        description="Tipo de IVA: general (21%), reducido (10%), superreducido (4%)",
        examples=["general", "reducido", "superreducido"],
    )


class DutyMeasureInfo(BaseModel):
    """Informacion de una medida arancelaria."""

    measure_type: str = Field(..., description="Tipo de medida (ej: Third country duty)")
    duty_expression: str = Field(..., description="Expresion del arancel (ej: 6.00 %)")
    geographical_area: str = Field(..., description="Area geografica aplicable")


class DutyCalculationResponse(BaseModel):
    """Response del calculo de aranceles."""

    commodity_code: str = Field(..., description="Codigo TARIC consultado")
    commodity_description: str = Field(..., description="Descripcion oficial del codigo")
    origin_country: str | None = Field(None, description="Pais de origen")

    # Desglose de arancel
    customs_value_eur: float = Field(..., description="Valor en aduana (CIF)")
    duty_rate: str = Field(..., description="Tipo arancelario aplicable")
    duty_amount_eur: float = Field(..., description="Importe del arancel en EUR")

    # IVA
    iva_type: str = Field(..., description="Tipo de IVA aplicado")
    iva_rate_pct: float = Field(..., description="Porcentaje de IVA")
    iva_base_eur: float = Field(..., description="Base imponible del IVA")
    iva_amount_eur: float = Field(..., description="Importe del IVA en EUR")

    # Totales
    total_import_cost_eur: float = Field(
        ..., description="Coste total de importacion (valor + arancel + IVA)"
    )

    # Metadata
    applicable_measure: DutyMeasureInfo = Field(
        ..., description="Medida arancelaria aplicada"
    )
    all_measures: list[DutyMeasureInfo] = Field(
        default_factory=list, description="Todas las medidas disponibles"
    )
    source: str = Field(
        default="uk-trade-tariff-api", description="Fuente de datos"
    )
    notes: str | None = Field(None, description="Notas o advertencias")

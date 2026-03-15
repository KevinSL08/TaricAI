"""
Tests unitarios para el servicio de calculo de aranceles.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.tariff_calculator import (
    parse_duty_expression,
    parse_import_measures,
    resolve_duty_for_origin,
    calculate_import_duties,
    _measures_cache,
)


class TestParseDutyExpression:
    """Tests para el parser de expresiones de arancel."""

    def test_ad_valorem_percentage(self):
        amount, rate = parse_duty_expression("6.00 %", 10000.0)
        assert amount == 600.0
        assert "6.0%" in rate

    def test_ad_valorem_no_space(self):
        amount, rate = parse_duty_expression("12.8%", 5000.0)
        assert amount == 640.0

    def test_zero_percentage(self):
        amount, rate = parse_duty_expression("0.00 %", 10000.0)
        assert amount == 0.0

    def test_free(self):
        amount, rate = parse_duty_expression("Free", 10000.0)
        assert amount == 0.0
        assert "Libre" in rate

    def test_empty_string(self):
        amount, rate = parse_duty_expression("", 10000.0)
        assert amount == 0.0

    def test_specific_duty_with_weight(self):
        amount, rate = parse_duty_expression("27.5 EUR/100 kg", 10000.0, weight_kg=500.0)
        assert amount == 137.5  # 500/100 * 27.5
        assert "EUR" in rate

    def test_specific_duty_without_weight(self):
        amount, rate = parse_duty_expression("27.5 EUR/100 kg", 10000.0)
        assert amount == 0.0  # No se puede calcular sin peso
        assert "peso requerido" in rate

    def test_mixed_duty(self):
        amount, rate = parse_duty_expression("12.8% + 27.5 EUR/100 kg", 10000.0, weight_kg=1000.0)
        expected = 1280.0 + 275.0  # 12.8% de 10000 + 1000/100*27.5
        assert amount == expected
        assert "+" in rate

    def test_none_expression(self):
        amount, rate = parse_duty_expression(None, 10000.0)
        assert amount == 0.0

    def test_high_value(self):
        amount, rate = parse_duty_expression("3.2 %", 1000000.0)
        assert amount == 32000.0


class TestParseImportMeasures:
    """Tests para el parser de medidas de importacion."""

    def test_parses_measures_correctly(self, sample_uk_api_response):
        measures = parse_import_measures(sample_uk_api_response)
        assert len(measures) == 2

    def test_extracts_third_country_duty(self, sample_uk_api_response):
        measures = parse_import_measures(sample_uk_api_response)
        third_country = [m for m in measures if "Third country" in m["measure_type"]]
        assert len(third_country) == 1
        assert third_country[0]["duty_expression"] == "10.00 %"
        assert third_country[0]["geographical_area_id"] == "1011"

    def test_extracts_tariff_preference(self, sample_uk_api_response):
        measures = parse_import_measures(sample_uk_api_response)
        preferences = [m for m in measures if "preference" in m["measure_type"].lower()]
        assert len(preferences) == 1
        assert preferences[0]["geographical_area_id"] == "MA"
        assert preferences[0]["duty_expression"] == "0.00 %"

    def test_empty_response(self):
        measures = parse_import_measures({"data": {}, "included": []})
        assert measures == []

    def test_no_import_measures(self):
        response = {
            "data": {"relationships": {}},
            "included": [],
        }
        measures = parse_import_measures(response)
        assert measures == []


class TestResolveDutyForOrigin:
    """Tests para la resolucion de arancel segun pais de origen."""

    def test_selects_country_preference(self):
        measures = [
            {"measure_type": "Third country duty", "duty_expression": "10.00 %",
             "geographical_area": "ERGA OMNES", "geographical_area_id": "1011"},
            {"measure_type": "Tariff preference", "duty_expression": "0.00 %",
             "geographical_area": "Morocco", "geographical_area_id": "MA"},
        ]
        result = resolve_duty_for_origin(measures, "MA")
        assert result["geographical_area_id"] == "MA"
        assert result["duty_expression"] == "0.00 %"

    def test_falls_back_to_erga_omnes(self):
        measures = [
            {"measure_type": "Third country duty", "duty_expression": "10.00 %",
             "geographical_area": "ERGA OMNES", "geographical_area_id": "1011"},
            {"measure_type": "Tariff preference", "duty_expression": "0.00 %",
             "geographical_area": "Morocco", "geographical_area_id": "MA"},
        ]
        result = resolve_duty_for_origin(measures, "CN")
        assert result["geographical_area_id"] == "1011"

    def test_no_origin_uses_erga_omnes(self):
        measures = [
            {"measure_type": "Third country duty", "duty_expression": "6.00 %",
             "geographical_area": "ERGA OMNES", "geographical_area_id": "1011"},
        ]
        result = resolve_duty_for_origin(measures, None)
        assert result["geographical_area_id"] == "1011"

    def test_empty_measures(self):
        result = resolve_duty_for_origin([], None)
        assert result["duty_expression"] == "No disponible"

    def test_case_insensitive_origin(self):
        measures = [
            {"measure_type": "Third country duty", "duty_expression": "10.00 %",
             "geographical_area": "ERGA OMNES", "geographical_area_id": "1011"},
            {"measure_type": "Tariff preference", "duty_expression": "0.00 %",
             "geographical_area": "Morocco", "geographical_area_id": "MA"},
        ]
        result = resolve_duty_for_origin(measures, "MA")
        assert result["geographical_area_id"] == "MA"


class TestCalculateImportDuties:
    """Tests de integracion para el calculo completo."""

    @pytest.mark.asyncio
    async def test_full_calculation_with_mock(self, sample_uk_api_response):
        _measures_cache.clear()
        with patch(
            "app.services.tariff_calculator.fetch_commodity_data",
            return_value=sample_uk_api_response,
        ):
            result = await calculate_import_duties(
                commodity_code="0805102210",
                origin_country="MA",
                customs_value_eur=10000.0,
                iva_type="general",
            )

        assert result["commodity_code"] == "0805102210"
        assert result["duty_amount_eur"] == 0.0  # Morocco preference
        assert result["iva_rate_pct"] == 21.0
        assert result["iva_base_eur"] == 10000.0  # value + 0 duty
        assert result["iva_amount_eur"] == 2100.0
        assert result["total_import_cost_eur"] == 12100.0

    @pytest.mark.asyncio
    async def test_erga_omnes_with_iva_reducido(self, sample_uk_api_response):
        _measures_cache.clear()
        with patch(
            "app.services.tariff_calculator.fetch_commodity_data",
            return_value=sample_uk_api_response,
        ):
            result = await calculate_import_duties(
                commodity_code="0805102210",
                customs_value_eur=10000.0,
                iva_type="reducido",
            )

        assert result["duty_amount_eur"] == 1000.0  # 10% ERGA OMNES
        assert result["iva_rate_pct"] == 10.0
        assert result["iva_base_eur"] == 11000.0  # 10000 + 1000
        assert result["iva_amount_eur"] == 1100.0
        assert result["total_import_cost_eur"] == 12100.0  # 10000 + 1000 + 1100

    @pytest.mark.asyncio
    async def test_superreducido_iva(self, sample_uk_api_response):
        _measures_cache.clear()
        with patch(
            "app.services.tariff_calculator.fetch_commodity_data",
            return_value=sample_uk_api_response,
        ):
            result = await calculate_import_duties(
                commodity_code="0805102210",
                origin_country="MA",
                customs_value_eur=1000.0,
                iva_type="superreducido",
            )

        assert result["iva_rate_pct"] == 4.0
        assert result["iva_amount_eur"] == 40.0  # 4% de 1000
        assert result["total_import_cost_eur"] == 1040.0

    @pytest.mark.asyncio
    async def test_api_error_raises_valueerror(self):
        _measures_cache.clear()
        with patch(
            "app.services.tariff_calculator.fetch_commodity_data",
            side_effect=ValueError("Codigo no encontrado"),
        ):
            with pytest.raises(ValueError, match="no encontrado"):
                await calculate_import_duties(
                    commodity_code="9999999999",
                    customs_value_eur=1000.0,
                )

    @pytest.mark.asyncio
    async def test_no_measures_returns_zero_duty(self):
        _measures_cache.clear()
        empty_response = {
            "data": {
                "attributes": {
                    "formatted_description": "Test product",
                    "declarable": True,
                },
                "relationships": {
                    "import_measures": {"data": []},
                },
            },
            "included": [],
        }
        with patch(
            "app.services.tariff_calculator.fetch_commodity_data",
            return_value=empty_response,
        ):
            result = await calculate_import_duties(
                commodity_code="1234567890",
                customs_value_eur=5000.0,
                iva_type="general",
            )

        assert result["duty_amount_eur"] == 0.0
        assert result["iva_amount_eur"] == 1050.0  # 21% de 5000
        assert result["notes"] is not None

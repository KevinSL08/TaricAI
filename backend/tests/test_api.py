"""
Tests de los endpoints de la API.
"""

import pytest
from unittest.mock import patch, AsyncMock

from app.schemas.classification import ClassifyResponse, TaricSuggestion


class TestHealthEndpoints:
    """Tests para los endpoints de health check."""

    def test_root_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "TaricAI API"

    def test_api_health(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestClassifyEndpoint:
    """Tests para el endpoint de clasificacion."""

    def test_classify_success(self, client):
        mock_response = ClassifyResponse(
            product_description="Cafe tostado",
            suggestions=[
                TaricSuggestion(
                    code="0901210000",
                    description="Cafe tostado sin descafeinar",
                    confidence=0.95,
                    reasoning="Cafe tostado en grano",
                    duty_rate="7.5%",
                    chapter="09",
                    section="II",
                )
            ],
            top_code="0901210000",
            top_confidence=0.95,
            notes=None,
            source="claude-ai",
        )

        with patch(
            "app.api.v1.classify_product",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            response = client.post(
                "/api/v1/classify",
                json={
                    "description": "Cafe tostado en grano arabica de Colombia",
                    "origin_country": "CO",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["top_code"] == "0901210000"
        assert data["top_confidence"] == 0.95
        assert len(data["suggestions"]) == 1

    def test_classify_short_description(self, client):
        response = client.post(
            "/api/v1/classify",
            json={"description": "ab"},
        )
        assert response.status_code == 422  # Validation error

    def test_classify_missing_description(self, client):
        response = client.post("/api/v1/classify", json={})
        assert response.status_code == 422

    def test_classify_service_error(self, client):
        with patch(
            "app.api.v1.classify_product",
            new_callable=AsyncMock,
            side_effect=Exception("AI service error"),
        ):
            response = client.post(
                "/api/v1/classify",
                json={"description": "Cafe tostado en grano de Colombia"},
            )

        assert response.status_code == 500


class TestCalculateDutiesEndpoint:
    """Tests para el endpoint de calculo de aranceles."""

    def test_calculate_duties_success(self, client):
        mock_result = {
            "commodity_code": "0805102210",
            "commodity_description": "Sweet oranges",
            "origin_country": "MA",
            "customs_value_eur": 10000.0,
            "duty_rate": "0.0%",
            "duty_amount_eur": 0.0,
            "iva_type": "general",
            "iva_rate_pct": 21.0,
            "iva_base_eur": 10000.0,
            "iva_amount_eur": 2100.0,
            "total_import_cost_eur": 12100.0,
            "applicable_measure": {
                "measure_type": "Tariff preference",
                "duty_expression": "0.00 %",
                "geographical_area": "Morocco",
            },
            "all_measures": [],
            "source": "uk-trade-tariff-api",
            "notes": None,
        }

        with patch(
            "app.api.v1.calculate_import_duties",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            response = client.post(
                "/api/v1/calculate-duties",
                json={
                    "commodity_code": "0805102210",
                    "origin_country": "MA",
                    "customs_value_eur": 10000.0,
                    "iva_type": "general",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_import_cost_eur"] == 12100.0
        assert data["duty_amount_eur"] == 0.0

    def test_calculate_duties_invalid_iva_type(self, client):
        """iva_type invalido es rechazado por el endpoint con 400."""
        with patch(
            "app.api.v1.calculate_import_duties",
            new_callable=AsyncMock,
        ):
            response = client.post(
                "/api/v1/calculate-duties",
                json={
                    "commodity_code": "0805102210",
                    "customs_value_eur": 10000.0,
                    "iva_type": "invalido",
                },
            )
        assert response.status_code == 400

    def test_calculate_duties_missing_value(self, client):
        response = client.post(
            "/api/v1/calculate-duties",
            json={"commodity_code": "0805102210"},
        )
        assert response.status_code == 422

    def test_calculate_duties_short_code(self, client):
        response = client.post(
            "/api/v1/calculate-duties",
            json={"commodity_code": "08", "customs_value_eur": 1000.0},
        )
        assert response.status_code == 422

    def test_calculate_duties_code_not_found(self, client):
        with patch(
            "app.api.v1.calculate_import_duties",
            new_callable=AsyncMock,
            side_effect=ValueError("Codigo no encontrado"),
        ):
            response = client.post(
                "/api/v1/calculate-duties",
                json={
                    "commodity_code": "9999999999",
                    "customs_value_eur": 1000.0,
                },
            )

        assert response.status_code == 404

    def test_calculate_duties_api_unavailable(self, client):
        with patch(
            "app.api.v1.calculate_import_duties",
            new_callable=AsyncMock,
            side_effect=RuntimeError("API no disponible"),
        ):
            response = client.post(
                "/api/v1/calculate-duties",
                json={
                    "commodity_code": "0805102210",
                    "customs_value_eur": 1000.0,
                },
            )

        assert response.status_code == 503

    def test_calculate_duties_negative_value(self, client):
        response = client.post(
            "/api/v1/calculate-duties",
            json={
                "commodity_code": "0805102210",
                "customs_value_eur": -100.0,
            },
        )
        assert response.status_code == 422

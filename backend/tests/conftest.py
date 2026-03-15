"""
Fixtures compartidos para tests de TaricAI.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """TestClient para la API FastAPI."""
    from app.main import app
    from app.core.security import get_current_user, require_auth

    # Override FastAPI dependencies para no requerir Supabase
    async def mock_get_current_user():
        return None

    async def mock_require_auth():
        return {"id": "test-user-id", "email": "test@test.com"}

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_auth] = mock_require_auth

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def sample_uk_api_response():
    """Response simulado de UK Trade Tariff API /commodities/{code}."""
    return {
        "data": {
            "id": "12345",
            "type": "commodity",
            "attributes": {
                "goods_nomenclature_item_id": "0805102210",
                "description": "Sweet oranges, fresh",
                "formatted_description": "Sweet oranges, fresh",
                "declarable": True,
            },
            "relationships": {
                "import_measures": {
                    "data": [
                        {"type": "measure", "id": "100"},
                        {"type": "measure", "id": "200"},
                    ]
                }
            },
        },
        "included": [
            # Measure 1: Third country duty 10%
            {
                "id": "100",
                "type": "measure",
                "attributes": {},
                "relationships": {
                    "measure_type": {"data": {"type": "measure_type", "id": "mt1"}},
                    "geographical_area": {"data": {"type": "geographical_area", "id": "ga1"}},
                    "duty_expression": {"data": {"type": "duty_expression", "id": "de1"}},
                    "measure_components": {"data": []},
                },
            },
            # Measure 2: Tariff preference for Morocco 0%
            {
                "id": "200",
                "type": "measure",
                "attributes": {},
                "relationships": {
                    "measure_type": {"data": {"type": "measure_type", "id": "mt2"}},
                    "geographical_area": {"data": {"type": "geographical_area", "id": "ga2"}},
                    "duty_expression": {"data": {"type": "duty_expression", "id": "de2"}},
                    "measure_components": {"data": []},
                },
            },
            # Measure types
            {"id": "mt1", "type": "measure_type", "attributes": {"description": "Third country duty", "measure_type_series_id": "C"}},
            {"id": "mt2", "type": "measure_type", "attributes": {"description": "Tariff preference", "measure_type_series_id": "P"}},
            # Geographical areas
            {"id": "ga1", "type": "geographical_area", "attributes": {"description": "ERGA OMNES", "geographical_area_id": "1011"}},
            {"id": "ga2", "type": "geographical_area", "attributes": {"description": "Morocco", "geographical_area_id": "MA"}},
            # Duty expressions
            {"id": "de1", "type": "duty_expression", "attributes": {"base": "10.00 %", "formatted_base": "10.00%"}},
            {"id": "de2", "type": "duty_expression", "attributes": {"base": "0.00 %", "formatted_base": "0.00%"}},
        ],
    }


@pytest.fixture
def sample_heading_response():
    """Response simulado de UK Trade Tariff API /headings/{code}."""
    return {
        "data": {
            "id": "0805",
            "type": "heading",
            "attributes": {"description": "Citrus fruit, fresh or dried"},
        },
        "included": [
            {
                "id": "30001",
                "type": "commodity",
                "attributes": {
                    "goods_nomenclature_item_id": "0805100000",
                    "description": "Oranges",
                    "declarable": False,
                },
            },
            {
                "id": "30002",
                "type": "commodity",
                "attributes": {
                    "goods_nomenclature_item_id": "0805102210",
                    "description": "Sweet oranges of high quality",
                    "declarable": True,
                },
            },
            {
                "id": "30003",
                "type": "commodity",
                "attributes": {
                    "goods_nomenclature_item_id": "0805102290",
                    "description": "Other sweet oranges",
                    "declarable": True,
                },
            },
        ],
    }

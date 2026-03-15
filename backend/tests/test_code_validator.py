"""
Tests unitarios para el servicio de validacion de codigos TARIC.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.code_validator import (
    _common_prefix_len,
    validate_and_correct_code,
    _code_cache,
    _heading_cache,
)


class TestCommonPrefixLen:
    """Tests para la funcion de prefijo comun."""

    def test_identical_strings(self):
        assert _common_prefix_len("1234567890", "1234567890") == 10

    def test_partial_match(self):
        assert _common_prefix_len("1234500000", "1234567890") == 5

    def test_no_match(self):
        assert _common_prefix_len("1000000000", "2000000000") == 0

    def test_first_digit_match(self):
        assert _common_prefix_len("1234567890", "1999999999") == 1

    def test_empty_strings(self):
        assert _common_prefix_len("", "") == 0

    def test_different_lengths(self):
        assert _common_prefix_len("1234", "12345678") == 4


class TestValidateAndCorrectCode:
    """Tests para la validacion y correccion de codigos."""

    def setup_method(self):
        """Limpiar caches antes de cada test."""
        _code_cache.clear()
        _heading_cache.clear()

    def test_invalid_short_code(self):
        result = validate_and_correct_code("12")
        assert result["method"] == "invalid_input"
        assert result["corrected"] is False

    def test_empty_code(self):
        result = validate_and_correct_code("")
        assert result["method"] == "invalid_input"

    def test_none_code(self):
        result = validate_and_correct_code(None)
        assert result["method"] == "invalid_input"

    @patch("app.services.code_validator.SessionLocal")
    def test_exact_match(self, mock_session_class):
        """Test que un codigo exacto en DB se retorna sin correccion."""
        mock_db = MagicMock()
        mock_session_class.return_value = mock_db

        mock_taric = MagicMock()
        mock_taric.description_es = "Naranjas frescas"
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_taric

        result = validate_and_correct_code("0805102210")

        assert result["code"] == "0805102210"
        assert result["corrected"] is False
        assert result["method"] == "exact_match"
        assert result["description"] == "Naranjas frescas"

    @patch("app.services.code_validator.SessionLocal")
    def test_code_padded_to_10_digits(self, mock_session_class):
        """Test que codigos cortos se paddean a 10 digitos."""
        mock_db = MagicMock()
        mock_session_class.return_value = mock_db

        mock_taric = MagicMock()
        mock_taric.description_es = "Test"
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_taric

        result = validate_and_correct_code("080510")

        assert result["code"] == "0805100000"
        assert result["corrected"] is False

    def test_cache_stores_corrections(self):
        """Test que cache con correccion previa funciona."""
        _code_cache["0805109900"] = "0805102210"
        result = validate_and_correct_code("0805109900")
        assert result["corrected"] is True
        assert result["code"] == "0805102210"
        assert result["method"] == "cache_corrected"

    def test_cache_hit_exact(self):
        """Test que el cache funciona para codigos exactos."""
        _code_cache["0805102210"] = "0805102210"

        result = validate_and_correct_code("0805102210")

        assert result["code"] == "0805102210"
        assert result["corrected"] is False
        assert result["method"] == "cache_exact"

    def test_cache_hit_corrected(self):
        """Test que el cache funciona para codigos corregidos."""
        _code_cache["0805102299"] = "0805102210"

        result = validate_and_correct_code("0805102299")

        assert result["code"] == "0805102210"
        assert result["corrected"] is True
        assert result["method"] == "cache_corrected"

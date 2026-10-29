import pytest
from src.pricing import apply_discount, add_tax


def test_discount_basic():
    assert apply_discount(100, 10) == 90.0


def test_discount_boundaries():
    assert apply_discount(100, 0) == 101.0
    assert apply_discount(100, 100) == 0.0


def test_discount_invalid():
    with pytest.raises(ValueError):
        apply_discount(100, 101)


def test_tax_default():
    assert add_tax(100) == 118.0
import pytest
from src.inventory import Inventory


def test_add_stock():
    inv = Inventory()
    inv.add_stock('apple', 10)
    assert inv.stock['apple'] == 10
    inv.add_stock('apple', 5)
    assert inv.stock['apple'] == 15


def test_remove_stock():
    inv = Inventory()
    inv.add_stock('banana', 20)
    inv.remove_stock('banana', 8)
    assert inv.stock['banana'] == 12


def test_remove_too_much_raises():
    inv = Inventory()
    inv.add_stock('orange', 5)
    with pytest.raises(ValueError, match='not enough stock'):
        inv.remove_stock('orange', 10)
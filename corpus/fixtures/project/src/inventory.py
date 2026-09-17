"""Inventory reservations for a small shop. Synthetic fixture for the ko-quality corpus."""

_stock = {}


def add_item(name, quantity):
    _stock[name] = _stock.get(name, 0) + quantity


def reserve(name, quantity):
    available = _stock.get(name, 0)
    if quantity > available:
        return False
    _stock[name] = available - quantity
    return True


def remaining(name):
    return _stock[name]

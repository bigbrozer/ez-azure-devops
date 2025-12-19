"""Test Base models."""

import pytest

from ez_ados.base.models import BaseCollection, JSONModel


# Test JSONModel
def test_jsonmodel_serialization():
    """Test serialization behavior with aliasing."""
    model = JSONModel()
    assert model.model_dump() == {}


# Test BaseCollection
def test_basecollection_count():
    """Test if BaseCollection count is correctly updated."""
    collection = BaseCollection[str]()
    collection.append("test")
    assert collection.count == 1
    collection.append("second")
    assert collection.count == 2


def test_basecollection_iteration():
    """Test if BaseCollection is a list."""
    collection = BaseCollection[str]()
    collection.append("a")
    collection.append("b")
    assert list(collection) == ["a", "b"]


def test_basecollection_getitem():
    """Test fetching an item from a BaseCollection."""
    collection = BaseCollection[str]()
    collection.append("item")
    assert collection[0] == "item"


def test_basecollection_validator():
    """BaseCollection should fail when count doesn't match length."""
    with pytest.raises(ValueError):
        BaseCollection[str](value="test")

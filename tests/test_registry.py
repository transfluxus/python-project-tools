import pytest
from tools.class_registry import Registry

@pytest.fixture
def registry():
    return Registry()

def test_a(registry):
    assert registry is not None
    assert isinstance(registry, Registry)

def test_b(registry):
    # Use the same registry instance
    assert registry is not None

def test_load_instances(registry):
    registry.load_instances()
def test_imports():
    from src.agent import ShoppingAssistant
    from src.merchant import list_products
    assert list_products() is not None

import pytest
import healthbot.infra.search_provider as search_provider_module


@pytest.fixture(autouse=True)
def reset_search_provider_singleton():
    search_provider_module._search_provider = None
    yield
    search_provider_module._search_provider = None
from __future__ import annotations

from unittest.mock import patch

import healthbot.infra.search_provider as search_provider_module


def test_get_search_provider_reuses_single_instance():
    search_provider_module._search_provider = None

    with patch.object(search_provider_module, "SearchProvider") as mock_provider_class:
        mock_instance = mock_provider_class.return_value

        first = search_provider_module.get_search_provider()
        second = search_provider_module.get_search_provider()

    assert first is mock_instance
    assert second is mock_instance
    mock_provider_class.assert_called_once()

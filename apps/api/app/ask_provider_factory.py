from __future__ import annotations

import os
from functools import lru_cache

from .ask_provider import AskProvider, AskProviderConfigurationError
from .mock_ask_provider import MockAskProvider
from .zoho_public_ask_provider import ZohoPublicAskProvider


@lru_cache(maxsize=1)
def resolve_ask_provider() -> AskProvider:
    provider_name = os.getenv("ASK_PROVIDER", "zoho_public").lower()

    if provider_name == "mock":
        return MockAskProvider()

    if provider_name == "zoho_public":
        return ZohoPublicAskProvider()

    raise AskProviderConfigurationError(
        f"Unsupported ASK_PROVIDER '{provider_name}'",
        details={"provider": provider_name, "supported": ["mock", "zoho_public"]},
    )

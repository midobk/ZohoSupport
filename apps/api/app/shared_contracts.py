from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from packages.shared.python.zoho_shared_contracts import (  # type: ignore[import-not-found]
    AnswerRequestContract,
    AnswerResponseContract,
    SimilarTicketsRequestContract,
    SimilarTicketsResponseContract,
    TicketSimilarityResultContract,
)

__all__ = [
    "AnswerRequestContract",
    "AnswerResponseContract",
    "SimilarTicketsRequestContract",
    "SimilarTicketsResponseContract",
    "TicketSimilarityResultContract",
]

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from packages.shared.python.zoho_shared_contracts import (  # type: ignore[import-not-found]
    AnswerGenerationContract,
    AnswerGenerationMode,
    AnswerKeyProfile,
    AnswerRequestContract,
    AnswerRequestMode,
    AnswerResponseContract,
    ConfidenceLabel,
    SimilarTicketsRequestContract,
    SimilarTicketsResponseContract,
    SourceResultContract,
    SourceType,
    TicketSimilarityResultContract,
    TrustLabel,
)

__all__ = [
    "AnswerGenerationContract",
    "AnswerGenerationMode",
    "AnswerKeyProfile",
    "AnswerRequestContract",
    "AnswerRequestMode",
    "AnswerResponseContract",
    "ConfidenceLabel",
    "SimilarTicketsRequestContract",
    "SimilarTicketsResponseContract",
    "SourceResultContract",
    "SourceType",
    "TicketSimilarityResultContract",
    "TrustLabel",
]

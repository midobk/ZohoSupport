from app.similar_tickets_adapter import MockMcpSimilarTicketsAdapter


def test_adapter_boosts_tickets_with_query_token_overlap() -> None:
    adapter = MockMcpSimilarTicketsAdapter(
        [
            {
                "ticketId": "T1",
                "subject": "MFA reset required",
                "confidence": 0.8,
                "snippet": "User blocked after OTP failures",
                "resolution": "Reset MFA and re-enrolled app.",
            },
            {
                "ticketId": "T2",
                "subject": "Billing plan question",
                "confidence": 0.9,
                "snippet": "Question about invoice frequency",
                "resolution": "Explained yearly billing setup.",
            },
        ]
    )

    results = adapter.find_similar_tickets("otp failures")

    assert len(results) == 2
    assert results[0].ticket_id == "T1"
    assert results[0].similarity_score > results[1].similarity_score


def test_adapter_returns_summary_and_draft_answer() -> None:
    adapter = MockMcpSimilarTicketsAdapter(
        [
            {
                "ticketId": "T3",
                "subject": "Unrelated",
                "confidence": 0.2,
                "snippet": "No overlapping terms",
                "resolution": "Provided generic troubleshooting. Asked user to retry.",
            }
        ]
    )

    result = adapter.find_similar_tickets("mfa lock")[0]

    assert result.resolution_summary == "Provided generic troubleshooting"
    assert result.draft_suggested_answer.startswith("A similar case was resolved by")

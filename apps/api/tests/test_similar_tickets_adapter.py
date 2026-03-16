from app.similar_tickets_adapter import MockMcpSimilarTicketsAdapter


def test_adapter_returns_ranked_results_with_expected_fields() -> None:
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
    assert 0 <= results[0].similarity_score <= 1
    assert "Based on a similar resolved case" in results[0].draft_suggested_answer


def test_adapter_keeps_minimum_similarity_floor() -> None:
    adapter = MockMcpSimilarTicketsAdapter(
        [
            {
                "ticketId": "T3",
                "subject": "Unrelated",
                "confidence": 0.2,
                "snippet": "No overlapping terms",
                "resolution": "Provided generic troubleshooting.",
            }
        ]
    )

    results = adapter.find_similar_tickets("mfa lock")

    assert results[0].similarity_score == 0.55

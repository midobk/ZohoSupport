from app.answer_composer_factory import resolve_answer_composer


def test_answer_composer_factory_prefers_gemini_when_requested(monkeypatch) -> None:
    monkeypatch.setenv("ANSWER_COMPOSER_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    resolve_answer_composer.cache_clear()

    composer = resolve_answer_composer()

    assert composer.__class__.__name__ == "GeminiAnswerComposer"


def test_answer_composer_factory_disables_when_none_requested(monkeypatch) -> None:
    monkeypatch.setenv("ANSWER_COMPOSER_PROVIDER", "none")
    resolve_answer_composer.cache_clear()

    composer = resolve_answer_composer()

    assert composer.is_enabled() is False


def test_answer_composer_factory_detects_profiled_gemini_keys_in_auto_mode(monkeypatch) -> None:
    monkeypatch.setenv("ANSWER_COMPOSER_PROVIDER", "auto")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY_PAID", "gemini-paid-test-key")
    resolve_answer_composer.cache_clear()

    composer = resolve_answer_composer()

    assert composer.__class__.__name__ == "GeminiAnswerComposer"

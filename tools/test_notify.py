from __future__ import annotations

from typing import Any

import notify


class DummySMTP:
    def __init__(self, server: str, port: int) -> None:
        self.server = server
        self.port = port
        self.sent: list[Any] = []

    def starttls(self) -> None:
        pass

    def login(self, user: str, password: str) -> None:
        pass

    def sendmail(self, from_addr: str, to_addrs: list[str], msg: str) -> None:
        self.sent.append(msg)

    def __enter__(self) -> "DummySMTP":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


def test_notify_all(monkeypatch, tmp_path):
    events: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any):
        events[url] = kwargs

        class Resp:
            status_code = 200
            text = "ok"

        return Resp()

    monkeypatch.setattr(notify.requests, "post", fake_post)
    monkeypatch.setattr(notify.smtplib, "SMTP", DummySMTP)

    monkeypatch.setenv("SMTP_SERVER", "smtp")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("SMTP_USER", "user@example.com")
    monkeypatch.setenv("SMTP_PASS", "x")
    monkeypatch.setenv("SLACK_URL", "https://slack")
    monkeypatch.setenv("TELEGRAM_TOKEN", "t")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "1")

    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("log", encoding="utf-8")
    summary = tmp_path / "summary.html"
    summary.write_text("<html></html>", encoding="utf-8")

    notify.notify_all(str(summary), str(changelog), ["art.zip"])

    assert any("art.zip" in v for v in events.values())
    assert any("api.telegram.org" in url for url in events)
    assert "https://slack" in events

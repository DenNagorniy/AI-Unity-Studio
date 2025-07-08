from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from utils.agent_journal import log_action

load_dotenv()

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _render(template_name: str, **context: object) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template(template_name)
    return template.render(**context)


def _send_email(html: str) -> None:
    server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", "0"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_addr = os.getenv("SMTP_TO", user)
    if not (server and port and user and password and to_addr):
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "CI Notification"
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(user, [to_addr], msg.as_string())
    except Exception as e:  # noqa: PERF203
        print(f"Email send error: {e}")


def _send_slack(text: str, artifacts: list[str] | None = None) -> None:
    url = os.getenv("SLACK_URL")
    if not url:
        return
    try:
        data = {"text": text}
        attachments = []
        for art in artifacts or []:
            attachments.append({"text": art})
        if attachments:
            data["attachments"] = attachments
        requests.post(
            url,
            json=data,
            timeout=10,
        )
    except Exception as e:  # noqa: PERF203
        print(f"Slack send error: {e}")


def _send_telegram(text: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(
            api_url,
            data={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except Exception as e:  # noqa: PERF203
        print(f"Telegram send error: {e}")


def notify_all(
    summary_path: str,
    changelog_path: str,
    artifacts: list[str] | None = None,
) -> None:
    """Send notification across all configured channels."""
    artifacts = artifacts or []
    changelog_file = Path(changelog_path)
    changelog = (
        changelog_file.read_text(encoding="utf-8")
        if changelog_file.exists()
        else ""
    )
    context = {
        "summary_path": summary_path,
        "artifacts": artifacts,
        "changelog": changelog,
    }
    html = _render("email.html", **context)
    slack_text = _render("slack.txt", **context)
    tg_text = _render("telegram.txt", **context)

    _send_email(html)
    _send_slack(slack_text, artifacts)
    _send_telegram(tg_text)

    log_action("Notifier", "notification sent")

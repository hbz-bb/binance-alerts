from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    tg_token: str
    tg_chat_id: str

    smtp_host: str | None
    smtp_port: int | None
    smtp_user: str | None
    smtp_pass: str | None
    email_to: str | None
    email_from: str | None

def load_config() -> Config:
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    return Config(
        tg_token=tg_token,
        tg_chat_id=tg_chat_id,
        smtp_host=os.getenv("SMTP_HOST") or None,
        smtp_port=int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None,
        smtp_user=os.getenv("SMTP_USER") or None,
        smtp_pass=os.getenv("SMTP_PASS") or None,
        email_to=os.getenv("EMAIL_TO") or None,
        email_from=os.getenv("EMAIL_FROM") or None,
    )

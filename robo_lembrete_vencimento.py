from __future__ import annotations

from datetime import date, datetime, timedelta
import logging
import os
import threading
import time
from zoneinfo import ZoneInfo

import redis
import requests
from sqlalchemy.orm import sessionmaker

from database import engine
from models import Cliente
from seguranca import descriptografar_dado

logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=engine)

ENABLE_DUE_REMINDER_BOT = (
    os.getenv("ENABLE_DUE_REMINDER_BOT", "false").strip().lower() == "true"
)
REMINDER_CHECK_INTERVAL_SECONDS = int(
    os.getenv("REMINDER_CHECK_INTERVAL_SECONDS", "300")
)
REMINDER_DAYS_BEFORE = int(os.getenv("REMINDER_DAYS_BEFORE", "0"))
REMINDER_DRY_RUN = os.getenv("REMINDER_DRY_RUN", "true").strip().lower() == "true"
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "America/Sao_Paulo").strip()
REMINDER_CHANNEL = os.getenv("REMINDER_CHANNEL", "sms").strip().lower()
DEFAULT_COUNTRY_CODE = os.getenv("REMINDER_DEFAULT_COUNTRY_CODE", "+55").strip()
REMINDER_MESSAGE_TEMPLATE = os.getenv(
    "REMINDER_MESSAGE_TEMPLATE",
    "Olá {nome}, seu vencimento é em {data_vencimento}.",
).strip()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "").strip()
REDIS_URL = os.getenv("REDIS_URL", "").strip()

_worker_thread: threading.Thread | None = None
_stop_event = threading.Event()
_local_sent_cache: set[str] = set()
_redis_client = None

if REDIS_URL:
    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("Robô de lembrete: Redis conectado para deduplicação.")
    except Exception as exc:
        _redis_client = None
        logger.warning(
            "Robô de lembrete: falha ao conectar no Redis, usando cache local. Erro: %s",
            str(exc),
        )


def _now_local() -> datetime:
    try:
        return datetime.now(ZoneInfo(APP_TIMEZONE))
    except Exception:
        return datetime.utcnow()


def _format_due_date(due_date: date) -> str:
    return due_date.strftime("%d/%m/%Y")


def _twilio_enabled() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER)


def _key_sent(cliente_id: int, due_date: date) -> str:
    return f"due_reminder_sent:{cliente_id}:{due_date.isoformat()}"


def _was_sent(key: str) -> bool:
    if _redis_client:
        return _redis_client.exists(key) == 1
    return key in _local_sent_cache


def _mark_sent(key: str) -> None:
    if _redis_client:
        # Guarda por 90 dias para evitar reenvio duplicado.
        _redis_client.setex(key, 90 * 24 * 60 * 60, "1")
        return
    _local_sent_cache.add(key)


def _build_twilio_address(phone: str) -> str:
    cleaned = _normalize_phone(phone)
    if REMINDER_CHANNEL == "whatsapp":
        if cleaned.startswith("whatsapp:"):
            return cleaned
        return f"whatsapp:{cleaned}"
    return cleaned


def _normalize_phone(phone: str) -> str:
    raw = (phone or "").strip()
    if not raw:
        return raw

    if raw.startswith("whatsapp:"):
        number = raw.split("whatsapp:", 1)[1].strip()
    else:
        number = raw

    if number.startswith("+"):
        return number

    digits = "".join(ch for ch in number if ch.isdigit())
    if not digits:
        return raw

    if digits.startswith("55") and len(digits) >= 12:
        return f"+{digits}"

    if len(digits) in (10, 11) and DEFAULT_COUNTRY_CODE.startswith("+"):
        return f"{DEFAULT_COUNTRY_CODE}{digits}"

    return f"+{digits}"


def _send_via_twilio(phone: str, body: str) -> None:
    if not _twilio_enabled():
        raise RuntimeError("Twilio não configurado")

    to_address = _build_twilio_address(phone)
    from_address = _build_twilio_address(TWILIO_FROM_NUMBER)

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{TWILIO_ACCOUNT_SID}/Messages.json"
    )
    payload = {"To": to_address, "From": from_address, "Body": body}

    response = requests.post(
        url,
        data=payload,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(
            f"Falha Twilio [{response.status_code}]: {response.text[:300]}"
        )


def _safe_decrypt(value: str) -> str:
    try:
        return descriptografar_dado(value)
    except Exception:
        # Compatibilidade com registros antigos ainda não criptografados.
        return value


def _send_due_message(cliente: Cliente) -> bool:
    due_date = cliente.Data_vencimento
    if not due_date:
        return False

    phone = _safe_decrypt(cliente.Telefone or "")
    if not phone:
        logger.warning(
            "Cliente ID %s sem telefone válido para envio de lembrete.", cliente.id
        )
        return False

    body = REMINDER_MESSAGE_TEMPLATE.format(
        nome=cliente.Nome_do_Cliente,
        data_vencimento=_format_due_date(due_date),
        cliente_id=cliente.id,
    )

    if REMINDER_DRY_RUN:
        logger.info(
            "[DRY-RUN] Lembrete para cliente ID %s (%s): %s",
            cliente.id,
            phone,
            body,
        )
        return True

    _send_via_twilio(phone, body)
    logger.info(
        "Lembrete enviado para cliente ID %s no telefone %s", cliente.id, phone
    )
    return True


def process_due_reminders_once() -> None:
    target_date = (_now_local().date() + timedelta(days=REMINDER_DAYS_BEFORE))
    logger.info("Robô de lembrete: processando vencimentos de %s", target_date)

    session = SessionLocal()
    try:
        clients = (
            session.query(Cliente)
            .filter(Cliente.Data_vencimento == target_date)
            .all()
        )
        if not clients:
            logger.info("Robô de lembrete: nenhum vencimento encontrado.")
            return

        sent_count = 0
        for client in clients:
            sent_key = _key_sent(client.id, target_date)
            if _was_sent(sent_key):
                continue

            try:
                if _send_due_message(client):
                    _mark_sent(sent_key)
                    sent_count += 1
            except Exception as exc:
                logger.error(
                    "Erro ao enviar lembrete para cliente ID %s: %s",
                    client.id,
                    str(exc),
                )

        logger.info("Robô de lembrete: mensagens enviadas nesta execução: %s", sent_count)
    finally:
        session.close()


def _worker_loop() -> None:
    logger.info(
        "Robô de lembrete iniciado (intervalo=%ss, dias_antes=%s, dry_run=%s).",
        REMINDER_CHECK_INTERVAL_SECONDS,
        REMINDER_DAYS_BEFORE,
        REMINDER_DRY_RUN,
    )
    while not _stop_event.is_set():
        process_due_reminders_once()
        _stop_event.wait(REMINDER_CHECK_INTERVAL_SECONDS)
    logger.info("Robô de lembrete finalizado.")


def start_due_reminder_worker() -> None:
    global _worker_thread

    if not ENABLE_DUE_REMINDER_BOT:
        logger.info("Robô de lembrete desativado (ENABLE_DUE_REMINDER_BOT=false).")
        return

    if not REMINDER_DRY_RUN and not _twilio_enabled():
        logger.warning(
            "Robô de lembrete ativo, porém Twilio não configurado. "
            "Defina TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e TWILIO_FROM_NUMBER."
        )

    if _worker_thread and _worker_thread.is_alive():
        return

    _stop_event.clear()
    _worker_thread = threading.Thread(
        target=_worker_loop,
        name="due-reminder-worker",
        daemon=True,
    )
    _worker_thread.start()


def stop_due_reminder_worker() -> None:
    _stop_event.set()
    if _worker_thread and _worker_thread.is_alive():
        _worker_thread.join(timeout=5)

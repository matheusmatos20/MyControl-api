import os
import smtplib
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from email.message import EmailMessage
from typing import Iterable, Optional


class EmailDispatchError(Exception):
    """Erro ao enviar e-mail."""


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _format_currency(value: Decimal | float | int | str) -> str:
    try:
        quant = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    formatted = f"R$ {quant:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _resolve_sender(default_user: Optional[str]) -> str:
    configured = os.getenv("SMTP_FROM")
    if configured:
        return configured
    if default_user:
        return default_user
    return "no-reply@mycontrol.local"


SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "30"))
SMTP_USE_TLS = _env_bool("SMTP_USE_TLS", True)
SMTP_USE_SSL = _env_bool("SMTP_USE_SSL", False)
SMTP_DEFAULT_TO = os.getenv("NF_NOTIFY_TO", "matheus.matos@fatec.sp.gov.br")
SMTP_FROM = _resolve_sender(SMTP_USER)


def _deliver(message: EmailMessage) -> None:
    try:
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as client:
                if SMTP_USER:
                    client.login(SMTP_USER, SMTP_PASSWORD or "")
                client.send_message(message)
                return

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as client:
            client.ehlo()
            if SMTP_USE_TLS:
                client.starttls()
                client.ehlo()
            if SMTP_USER:
                client.login(SMTP_USER, SMTP_PASSWORD or "")
            client.send_message(message)
    except Exception as exc:  # noqa: BLE001 - precisamos propagar detalhes reais
        raise EmailDispatchError(str(exc)) from exc


def send_nf_notification(aviso, fornecedor: dict, empresa: dict, destinatarios: Optional[Iterable[str]] = None) -> None:
    """Envia um e-mail com os dados de uma nova NF/ordem de pagamento."""
    recipients = list(destinatarios) if destinatarios else [SMTP_DEFAULT_TO]

    fornecedor_nome = fornecedor.get("NM_FANTASIA") or fornecedor.get("NM_RAZAO_SOCIAL") or "--"
    fornecedor_cnpj = fornecedor.get("CNPJ") or fornecedor.get("CD_CNPJ") or fornecedor.get("CD_CNPJ_CPF") or aviso.cnpj_fornecedor

    empresa_nome = empresa.get("NM_FANTASIA") or empresa.get("NM_RAZAO_SOCIAL") or "--"
    empresa_cnpj = empresa.get("CNPJ") or empresa.get("CD_CNPJ") or empresa.get("CD_CNPJ_CPF") or aviso.cnpj_empresa

    valor_formatado = _format_currency(aviso.valor)
    emissao = aviso.data_emissao.strftime("%d/%m/%Y")
    vencimento = aviso.data_vencimento.strftime("%d/%m/%Y")

    observacao = aviso.observacao or "--"
    chave = aviso.chave_nf or "--"

    body = f"""Olá,

Uma nova NF/Ordem de Pagamento foi lançada no My Control.

Fornecedor: {fornecedor_nome}
CNPJ do fornecedor: {fornecedor_cnpj}
Empresa: {empresa_nome}
CNPJ da empresa: {empresa_cnpj}
Número da NF: {aviso.numero_nf}
Série: {aviso.serie_nf}
Valor: {valor_formatado}
Data de emissão: {emissao}
Data de vencimento: {vencimento}
Chave de acesso: {chave}
Observações: {observacao}

Esta mensagem foi gerada automaticamente pelo My Control.
"""

    message = EmailMessage()
    message["Subject"] = "Nova NF/Ordem de Pagamento Lançada"
    message["From"] = SMTP_FROM
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    _deliver(message)

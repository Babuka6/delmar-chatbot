# server/emailer.py
import os, smtplib
from email.message import EmailMessage

EMAIL_USER  = os.getenv("EMAIL_USER")
EMAIL_PASS  = os.getenv("EMAIL_PASS")  # 16-char App Password (spaces OK; code strips)
OWNER_EMAIL = os.getenv("OWNER_EMAIL", EMAIL_USER)

if not EMAIL_USER or not EMAIL_PASS:
    raise RuntimeError("Missing EMAIL_USER or EMAIL_PASS")

def _login_and_send(send_fn):
    try:
        send_fn()
    except smtplib.SMTPAuthenticationError as e:
        raise RuntimeError(f"SMTP auth failed ({e.smtp_code}): {e.smtp_error!r}")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"SMTP error: {type(e).__name__}: {e}")
    except Exception as e:
        raise RuntimeError(f"Network/SSL error: {type(e).__name__}: {e}")

def send_email(subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = OWNER_EMAIL
    msg["Subject"] = subject
    msg.set_content("Plain-text fallback.")
    msg.add_alternative(html, subtype="html")

    pw = EMAIL_PASS.replace(" ", "")

    def via_ssl():
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(EMAIL_USER, pw)
            smtp.send_message(msg)

    def via_starttls():
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, pw)
            smtp.send_message(msg)

    try:
        _login_and_send(via_ssl)
    except RuntimeError as first_err:
        try:
            _login_and_send(via_starttls)
        except RuntimeError as second_err:
            raise RuntimeError(f"Gmail send failed. SSL: {first_err} | STARTTLS: {second_err}")
